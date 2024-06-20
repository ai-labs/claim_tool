# import uuid
import logging

from fastapi import APIRouter
from fastapi.responses import UJSONResponse
from fastapi.datastructures import UploadFile

from ailabs.claims.database.models import DOCUMENT

from . import models


router = APIRouter(prefix="/documents")


@router.post("/{claim}")
async def submit(
    claim: models.Claim.Fetch.model_fields["ID"].annotation,  # noqa: F821
    documents: list[UploadFile],
) -> UJSONResponse:
    items: dict[str, DOCUMENT] = {}

    for document in documents:
        item = DOCUMENT(
            claim=claim,
            name=document.filename,
            type=document.content_type,
            data=await document.read(),
        )

        await item.save()

        items[document.filename] = item.model_dump(exclude=["data"])

    return items


logger = logging.getLogger(__name__)
