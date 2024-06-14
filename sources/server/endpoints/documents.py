import logging

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import UJSONResponse
from fastapi.datastructures import UploadFile

from . import models


router = APIRouter(prefix="/documents")


@router.post("/{claim}")
async def submit(
    request: Request,
    claim: models.Claim.model_fields["ID"].annotation,  # noqa: F821
    documents: list[UploadFile],
) -> UJSONResponse:
    storage = request.app.state.storage

    bucket = (await storage.append(claim, documents)).copy()

    return {name: timestamp for name, (_, _, timestamp) in bucket.items()}


logger = logging.getLogger(__name__)
