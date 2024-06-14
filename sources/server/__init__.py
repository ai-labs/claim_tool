import queue
import asyncio
import logging
import importlib
import contextlib

from types import ModuleType
from typing import Awaitable
from dataclasses import dataclass

from openai import OpenAI
from fastapi import FastAPI

from ailabs.claims import settings
from ailabs.claims.vendor import outlines


@dataclass
class Config:

    server: settings.Server

    general: settings.General


class Tasks:

    exits: bool = False

    tasks: set[asyncio.Task]

    def __init__(self) -> None:
        self.loop, self.tasks = asyncio.get_running_loop(), set()

    def callback(self, future: asyncio.Future) -> None:
        try:
            future.result()
        except asyncio.CancelledError:
            pass
        except BaseException as error:
            logger.error("Error in background task", exc_info=(type(error), error, error.__traceback__.tb_next))
            raise

    def add(self, awaitable: Awaitable) -> asyncio.Task:
        if self.exits:
            message = "Can not add new tasks on shutdown"
            raise RuntimeError(message)
        task = self.loop.create_task(awaitable)
        task.add_done_callback(self.tasks.discard)
        task.add_done_callback(self.callback)
        self.tasks.add(task)
        return task

    def cancel(self) -> None:
        if self.exits:
            return

        self.exits = True
        queue.deque(task.cancel() for task in self.tasks)
        self.exits = False



@contextlib.asynccontextmanager
async def lifespan(application: FastAPI) -> None:
    """
    ASGI lifespan context for startup/shutdown events.
    """
    class LineSuppressFilter(logging.Filter):
        """
        After added to the logger, suppress one line and remove itself from it.
        """
        def filter(self, record) -> bool:
            logger = logging.getLogger(record.name)
            logger.removeFilter(self)
            return False

    async def loadmodule(name: str, *args, **kwargs) -> ModuleType:
        try:
            if hasattr((module := importlib.import_module(f".{name}", __package__)), "initialize"):
                await module.initialize(application, *args, **kwargs)
            return module
        except Exception as error:
            logger.error("Failed to load module: %s", name, exc_info=error)
            raise asyncio.CancelledError from error

    suppressor = LineSuppressFilter()

    # allow arbitrary background tasks
    tasks = application.state.tasks = Tasks()

    try:

        config: Config = application.state.config

        if not isinstance(config, Config):
            required, actual = Config.__qualname__, type(config).__qualname__
            message = f"server config must be of {required} type, not {actual}"
            raise TypeError(message)

        # load endpoints
        application.include_router((await loadmodule("endpoints")).router)

        # create OpenAI client
        application.state.openai = OpenAI(api_key=config.general.token.get_secret_value())

    except asyncio.CancelledError:
        logging.getLogger("uvicorn.error").addFilter(suppressor)
        raise

    except BaseException as error:
        logger.error("Error at server startup", exc_info=error)
        logging.getLogger("uvicorn.error").addFilter(suppressor)
        raise

    yield

    application.state.openai.close()

    try:
        tasks.cancel()
    except BaseException as error:
        logger.error("Error at server shutdown", exc_info=error)
        logging.getLogger("uvicorn.error").addFilter(suppressor)
        raise


root = FastAPI(
    lifespan=lifespan,
    title=outlines.metadata["Name"],
    description=outlines.metadata["Summary"],
)


logger = logging.getLogger(__name__)
