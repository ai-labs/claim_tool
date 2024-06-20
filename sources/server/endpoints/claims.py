from fastapi import APIRouter, status
from fastapi.responses import UJSONResponse
from fastapi.exceptions import HTTPException

from ailabs.claims.database.models import CLAIM, RESULT

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


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[models.Claim.Full],
)
async def fetch() -> UJSONResponse:
    claims = []

    for item in await CLAIM.all().to_list():
        claim = models.Claim.Full.from_orm(item)
        result = await RESULT.find_one(RESULT.ID == claim.ID)
        claim.result = models.Result.Nested.from_orm(result) if result else None
        claims.append(claim)

    return claims


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=models.Claim.Fetch,
)
async def submit(
    claim: models.Claim.Submit,
) -> UJSONResponse:
    return await CLAIM(**claim.dict() | {"status": "PENDING"}).insert()


@router.patch(
    "/{claim}",
    status_code=status.HTTP_200_OK,
    response_model=models.Claim.Fetch,
)
async def update(
    claim: models.Claim.Fetch.model_fields["ID"].annotation,  # noqa: F821
    update: models.Claim.Update,
) -> UJSONResponse:
    claim = await CLAIM.find_one(CLAIM.ID == claim)

    if update.status and update.status != "OPEN" and claim.status == "PENDING":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Pending claims status can be changed only to OPEN, not {update.status}",
        )

    if claim is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Specified claim does not exist",
        )

    await claim.update({"$set": update.model_dump(exclude_defaults=True, exclude_unset=True)})

    return claim
