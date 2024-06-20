import uuid

from enum import Enum
from typing import Literal, Annotated
from datetime import date, datetime, timezone

from pydantic import Field, BaseModel, ConfigDict

from ailabs.claims.database.models import RESULT


class Result:
    class Nested(BaseModel):
        model_config: ConfigDict = ConfigDict(
            from_attributes=True,
        )

        status: Annotated[
            RESULT.Status,
            Field(description="Suggested claim status."),
        ]

        reason: Annotated[
            RESULT.Reason | None,
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

        damage: Annotated[
            RESULT.Damage | None,
            Field(description="Damage properties."),
        ] = None

    class Fetch(Nested):
        ID: Annotated[
            uuid.UUID,
            Field(
                description="Claim identifier this result belongs to.",
            ),
        ]


class Claim:
    class Update(BaseModel):
        model_config: ConfigDict = ConfigDict(
            validate_assignment=True,
            validate_default=True,
            use_enum_values=True,
        )

        status: Annotated[
            Literal["OPEN", "IN_PROGRESS", "CLOSED"] | None,
            Field(description="Current status of the claim."),
        ] = None

        document: Annotated[
            uuid.UUID | None,
            Field(description="Document number related to the claim."),
        ] = None

        documents: Annotated[
            list[uuid.UUID],
            Field(
                default_factory=list,
                description="References to related documents, such as images, invoices, or additional details.",
            ),
        ]

    class Submit(Update):
        # model_config: ConfigDict = ConfigDict(
        #     validate_assignment=True,
        #     validate_default=True,
        #     use_enum_values=True,
        # )

        customer: Annotated[
            uuid.UUID,
            Field(description="Identifier for the customer submitting the claim."),
        ]

        date: Annotated[
            date,
            Field(
                default_factory=lambda: datetime.now(timezone.utc).date(),
                description="Date when the claim was submitted.",
            ),
        ]

        type: Annotated[
            Literal["RETURN", "COMPLAINT", "DISPUTE"],
            Field(description="Type of claim."),
        ]

        description: Annotated[
            str,
            Field(description="Description of the claim."),
        ]

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

    class Fetch(Submit):
        ID: Annotated[
            uuid.UUID,
            Field(description="Unique identifier for each claim."),
        ]

        date: Annotated[
            date,
            Field(
                description="Date when the claim was submitted.",
            ),
        ]

        status: Annotated[
            Literal["PENDING", "OPEN", "IN_PROGRESS", "CLOSED"],
            Field(description="Current status of the claim."),
        ]

        created: Annotated[
            date,
            Field(description="Date when the claim record was created."),
        ]
        updated: Annotated[
            date,
            Field(description="Date when the claim record was last updated."),
        ]

    class Full(Fetch):
        model_config: ConfigDict = ConfigDict(
            from_attributes=True,
        )

        result: Annotated[
            Result.Nested | None,
            Field(description="AI processing result, if available."),
        ] = None


class Answer(BaseModel):
    model_config: ConfigDict = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        use_enum_values=True,
    )

    class Status(Enum):
        APPROVED: str = "APPROVED"
        REJECTED: str = "REJECTED"
        RESEARCH: str = "RESEARCH"

    status: Annotated[
        Status,
        Field(description="Suggested claim status."),
    ]

    class Reason(Enum):
        # APPROVED
        CLAIM_AMOUNT_BELOW_THRESHOLD: str = "CLAIM_AMOUNT_BELOW_THRESHOLD"
        # REJECTED
        DESCRIPTION_MISMATCH: str = "DESCRIPTION_MISMATCH"
        NOT_ENOUGH_DOCUMENTS: str = "NOT_ENOUGH_DOCUMENTS"
        NOT_ENOUTH_DATA: str = "NOT_ENOUTH_DATA"

    reason: Annotated[
        None | Reason,
        Field(description="Status change reason."),
    ] = None

    class Document(BaseModel):
        type: Annotated[
            Literal["INVOICE", "PRODUCT", "OTHER"],
            Field(description="Detected type of the attached document."),
        ]

        text: Annotated[
            str,
            Field(description="Text representation of the attached document."),
        ]

        class Damage(BaseModel):
            product: Annotated[
                str,
                Field(description="Detected product name."),
            ]

            damaged: Annotated[
                float,
                Field(description="Damage percent.", ge=0.0, le=1.0),
            ]

            damages: Annotated[
                list[str],
                Field(description="Types of damages detected."),
            ]

        damage: Annotated[Damage | None, Field(description="Extra info about damaged product.")] = None

    extra: Annotated[
        dict[str, Document] | None,
        Field(description="Extra info extracted by LLM."),
    ] = None
