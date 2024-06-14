import asyncio
import logging

from pathlib import Path
from datetime import datetime, timezone, timedelta

import aiofiles
import aioshutil

from fastapi import FastAPI, APIRouter
from fastapi.datastructures import UploadFile

from . import claims, documents


router = APIRouter(prefix="")


router.include_router(claims.router)
router.include_router(documents.router)


class Storage:

    lock: asyncio.Lock

    root: Path

    documents: dict[int, dict[str, (str, Path, datetime)]]

    def __init__(self, root: Path) -> None:
        root.mkdir(parents=True, exist_ok=True)
        self.documents, self.root = {}, root
        self.lock = asyncio.Lock()

    def get(self, claim: int) -> dict[str, (datetime, Path)]:
        return self.documents.get(claim, {})

    async def append(self, claim: int, documents: list[UploadFile]) -> dict[str, (str, Path, datetime)]:
        async with self.lock:
            loop = asyncio.get_event_loop()
            root = self.root/str(claim)
            root.mkdir(exist_ok=True)

            bucket = self.documents.pop(claim, {})
            timestamp = datetime.now(timezone.utc)

            pending: set[asyncio.Future] = {
                loop.create_task(self.save(file, root/file.filename)) for file in documents
            }

            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

                for future in done:
                    await (document := future.result()).close()
                    bucket[document.filename] = (document.content_type, root/document.filename, timestamp)

            self.documents[claim] = bucket

        return bucket

    async def remove(self, claim: int) -> None:
        async with self.lock:
            await aioshutil.rmtree(self.root/str(claim), ignore_errors=True)
            del self.documents[claim]

    async def save(self, document: UploadFile, path: Path) -> UploadFile:
        """
        Copy temporary file to more persistent storage.

        Parameters
        ----------
        document : UploadFile
            Uploaded file to be copied.

        Returns
        -------
        UploadFile
           Uploaded file itself for calls chaining.
        """
        async with aiofiles.open(path, "wb") as target:
            while chunk := await document.read():
                await target.write(chunk)
        return document

    async def housekeeper(self, interval: float = 60.0) -> None:
        logger.info("Housekeeper task started")
        while await asyncio.sleep(interval, True):
            logger.debug("Running storage cleanup")
            async with self.lock:
                for claim in tuple(self.documents):
                    bucket = self.documents[claim]

                    for name in tuple(bucket):
                        _, path, timestamp = bucket[name]

                        if (datetime.now(timezone.utc) - timestamp) <= timedelta(minutes=5):
                            continue

                        del bucket[name]
                        path.unlink()

                    if not bucket:
                        (self.root/str(claim)).rmdir()
                        del self.documents[claim]


async def initialize(server: FastAPI) -> None:
    appdir = server.state.appdir

    server.state.storage = storage = Storage(appdir.cache/"documents")

    server.state.tasks.add(storage.housekeeper())


logger = logging.getLogger(__name__)
