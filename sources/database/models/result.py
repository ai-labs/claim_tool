import enum
import uuid

from typing import Annotated

from beanie import Document
from pymongo import ASCENDING, IndexModel
from pydantic import Field, BaseModel


class RESULT(Document):
    class Settings:
        name = "results"

        validate_on_save = True

        indexes = [  # noqa: RUF012
            IndexModel([("ID", ASCENDING)], unique=True),
        ]

    ID: Annotated[
        uuid.UUID,
        Field(
            description="Claim identifier this result belongs to.",
        ),
    ]

    class Status(enum.Enum):
        APPROVED: str = "APPROVED"
        REJECTED: str = "REJECTED"
        RESEARCH: str = "RESEARCH"

    status: Annotated[
        Status,
        Field(description="Suggested claim status."),
    ]

    class Reason(enum.Enum):
        # APPROVED
        CLAIM_AMOUNT_BELOW_THRESHOLD: str = "CLAIM_AMOUNT_BELOW_THRESHOLD"
        # REJECTED
        NOT_RELEVANT: str = "NOT_RELEVANT"
        NOT_ENOUGH_DOCUMENTS: str = "NOT_ENOUGH_DOCUMENTS"
        NOT_ENOUTH_DATA: str = "NOT_ENOUTH_DATA"

    reason: Annotated[
        Reason | None,
        Field(description="Status change reason."),
    ] = None

    relevant: Annotated[
        bool | None,
        Field(description="Are provided documents relevant to the claim."),
    ] = None

    summary: Annotated[
        str | None,
        Field(description="Main document description."),
    ] = None

    description: Annotated[
        str | None,
        Field(description="Description of the other attached documents."),
    ] = None

    department: Annotated[
        str | None,
        Field(description="Recommendation of the department for this claim."),
    ] = None

    class Damage(BaseModel):
        factor: Annotated[
            float,
            Field(description="Damage factor, 0 means no damage.", ge=0.0, le=1.0),
        ]

        damage: Annotated[
            str,
            Field(description="Damages description."),
        ]

    damage: Annotated[
        Damage | None,
        Field(description="Damage properties."),
    ] = None
