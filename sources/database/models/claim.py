import uuid

from typing import Literal, Annotated
from datetime import date, datetime, timezone

from beanie import Insert, Update, Document, before_event
from pymongo import ASCENDING, IndexModel
from pydantic import Field


class CLAIM(Document):
    class Settings:
        name = "claims"

        validate_on_save = True

        indexes = [  # noqa: RUF012
            IndexModel([("ID", ASCENDING)], unique=True),
        ]

    ID: Annotated[
        uuid.UUID,
        Field(
            default_factory=uuid.uuid4,
            description="Unique identifier for each claim.",
        ),
    ]

    customer: Annotated[
        uuid.UUID,
        Field(description="Identifier for the customer submitting the claim."),
    ]

    date: Annotated[
        date,
        Field(description="Date when the claim was submitted."),
    ]

    type: Annotated[
        Literal["RETURN", "COMPLAINT", "DISPUTE"],
        Field(description="Type of claim."),
    ]

    description: Annotated[
        str,
        Field(description="Description of the claim."),
    ]

    document: Annotated[
        uuid.UUID | None,
        Field(description="Document number related to the claim."),
    ] = None

    material: Annotated[
        int | None,
        Field(description="Material number of the claimed item."),
    ] = None

    quantity: Annotated[
        float,
        Field(description="Quantity of the claimed item."),
    ]

    unit: Annotated[
        str,
        Field(description="Unit of measure for the claimed item."),
    ]

    amount: Annotated[
        float,
        Field(description="Monetary value of the claim."),
    ]

    status: Annotated[
        Literal["PENDING", "OPEN", "IN_PROGRESS", "CLOSED"],
        Field(description="Current status of the claim."),
    ]

    created: Annotated[
        date,
        Field(
            default_factory=lambda: datetime.now(timezone.utc).date(),
            description="Date when the claim record was created.",
        ),
    ]
    updated: Annotated[
        date | None,
        Field(description="Date when the claim record was last updated."),
    ] = None

    @before_event(Insert)
    def add_updated(self) -> None:
        self.updated = self.created

    @before_event(Update)
    def set_updated(self) -> None:
        self.updated = datetime.now(timezone.utc).date()

    documents: Annotated[
        list[uuid.UUID],
        Field(description="References to related documents, such as images, invoices, or additional details."),
    ]
