import asyncio
import logging

from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, APIRouter

from ailabs.claims import openai
from ailabs.claims.server import Config
from ailabs.claims.database.models import CLAIM, RESULT, DOCUMENT

from . import claims, documents


router = APIRouter(prefix="")


router.include_router(claims.router)
router.include_router(documents.router)


async def analyzer(client: openai.OpenAI, config: Config) -> None:
    logger.info("Background task started: [bold cyan]analyzer[/]", extra={"markup": True})

    loop = asyncio.get_event_loop()

    tasks: dict[asyncio.Task, CLAIM] = {}

    async def analyze(claim: CLAIM) -> RESULT:
        document = None

        if claim.document:
            document = await DOCUMENT.find_one(DOCUMENT.ID == claim.document)

        documents = await DOCUMENT.find(
            DOCUMENT.claim == claim.ID,
        ).to_list()

        if document is not None:
            documents = list(filter(lambda item: item.ID != document.ID, documents))

        if document is None and not documents:
            answer = {"document": None, "response": None}

        else:
            with ThreadPoolExecutor(1) as executor:
                answer = await loop.run_in_executor(
                    executor,
                    openai.analyze,
                    client,
                    claim,
                    document,
                    documents,
                )

        claim.material = (answer["document"] or {}).get("material", claim.material)

        if answer["response"]:
            answer["response"]["damage"] = RESULT.Damage(**answer["response"].pop("damage"))

        result = RESULT(
            ID=claim.ID,
            status=RESULT.Status.RESEARCH,
            **answer["document"] or {"relevant": True},
            **answer["response"] or {},
        )

        if not answer["document"] and not answer["response"]:
            result.status = RESULT.Status.REJECTED
            result.reason = RESULT.Reason.NOT_ENOUGH_DOCUMENTS

        elif not result.relevant:
            result.status = RESULT.Status.REJECTED
            result.reason = RESULT.Reason.NOT_RELEVANT

        await result.insert()
        await claim.save()

        logger.info(result)
        logger.info(claim)

    def callback(future: asyncio.Future) -> None:
        if error := future.exception():
            logger.error("Failed to process claim", exc_info=error)
        tasks.pop(future)

    while await asyncio.sleep(config.general.interval, True):
        async for claim in CLAIM.find(CLAIM.status == "OPEN"):
            if claim in tasks.values():
                continue
            # skip already processed claims
            if (await RESULT.find_one(RESULT.ID == claim.ID)) is not None:
                continue

            # submit claims for processing
            task = loop.create_task(analyze(claim))
            tasks[task] = claim

            task.add_done_callback(callback)

        logger.debug("Currently processing claims: %s", len(tasks))


async def initialize(server: FastAPI) -> None:
    server.state.tasks.add(analyzer(server.state.openai, server.state.config))


logger = logging.getLogger(__name__)
