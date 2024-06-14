import asyncio

from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, status
from fastapi.requests import Request
from fastapi.responses import UJSONResponse
from fastapi.exceptions import HTTPException

from ailabs.claims import openai

from . import models


router = APIRouter(prefix="/claims")


NOT_ENOUTH_DOCUMENTS = models.Answer(
    status=models.Answer.Status.REJECTED,
    reason=models.Answer.Reason.NOT_ENOUGH_DOCUMENTS,
)

CLAIM_AMOUNT_BELOW_THRESHOLD = models.Answer(
    status=models.Answer.Status.APPROVED,
    reason=models.Answer.Reason.CLAIM_AMOUNT_BELOW_THRESHOLD,
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=models.Answer,
)
async def submit(
    request: Request,
    claim: models.Claim,
) -> UJSONResponse:
    client = request.app.state.openai
    config = request.app.state.config
    storage = request.app.state.storage

    documents = {
        name: data
        for name, data in storage.get(claim.ID).items()
        if name in claim.documents
    }

    if not claim.documents or not documents:
        return NOT_ENOUTH_DOCUMENTS

    if claim.amount < config.general.threshold:
        return CLAIM_AMOUNT_BELOW_THRESHOLD

    # convert documents to text

    loop = asyncio.get_event_loop()

    descriptions: dict[str, dict] = {}
    results: dict[str, dict] = {}

    with ThreadPoolExecutor() as executor:
        futures: dict[asyncio.Future, str] = {}

        for name, (content_type, path, _) in documents.items():
            future = loop.run_in_executor(
                executor,
                openai.describe,
                client,
                path,
                content_type,
            )
            futures[future] = name

        pending: set[asyncio.Future] = set(futures)

        while pending:
            done, pending = await asyncio.wait(pending)

            while done:
                future = done.pop()
                name = futures.pop(future)

                if name not in descriptions:
                    # get description and analyze it
                    description = future.result()
                    descriptions[name] = description

                    if description["type"] == "PRODUCT":
                        future = loop.run_in_executor(
                            executor,
                            openai.analyze,
                            client,
                            description,
                        )

                    futures[future] = name
                    pending.add(future)

                else:
                    # save analysis result
                    result = future.result()
                    results[name] = result

    data: dict[str, models.Answer.Document] = {}

    for name in descriptions:
        description = descriptions[name]

        damage = None

        if name in results:
            damage = models.Answer.Document.Damage(**results[name])

        document = models.Answer.Document(
            **description, damage=damage
        )

        data[name] = document

    answer = models.Answer(
        status=models.Answer.Status.RESEARCH,
        extra=data
    )

    try:
        return answer
    finally:
        await storage.remove(claim.ID)
