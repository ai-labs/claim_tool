import uuid

from beanie import Document
from pymongo import ASCENDING, IndexModel
from pydantic import Field


class DOCUMENT(Document):
    class Settings:
        name = "documents"

        validate_on_save = True

        indexes = [  # noqa: RUF012
            IndexModel([("ID", ASCENDING)], unique=True),
        ]

    ID: uuid.UUID = Field(default_factory=uuid.uuid4)

    claim: uuid.UUID

    name: str

    type: str

    data: bytes
