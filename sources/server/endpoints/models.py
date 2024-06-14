from enum import Enum
from typing import Literal, Annotated
from datetime import date

from pydantic import Field, BaseModel, ConfigDict


class Claim(BaseModel):
    model_config: ConfigDict = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        use_enum_values=True,
    )

    ID: Annotated[
        int,
        Field(description="Unique identifier for each claim."),
    ]

    customer: Annotated[
        int,
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
        int,
        Field(description="Document number related to the claim."),
    ]

    material: Annotated[
        int,
        Field(description="Material number of the claimed item."),
    ]

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
        Literal["OPEN", "IN_PROGRESS", "CLOSED"],
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

    documents: Annotated[
        list[str],
        Field(description="References to related documents, such as images, invoices, or additional details."),
    ]


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

        damage: Annotated[
            Damage | None,
            Field(description="Extra info about damaged product.")
        ] = None

    extra: Annotated[
        dict[str, Document] | None,
        Field(description="Extra info extracted by LLM."),
    ] = None
