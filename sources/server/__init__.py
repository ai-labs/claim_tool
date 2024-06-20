import asyncio
import logging
import contextlib

from dataclasses import dataclass

from openai import OpenAI
from fastapi import FastAPI

from ailabs.claims import settings, integrations
from ailabs.claims.vendor import outlines
from ailabs.claims.utilities import Tasks, LineSuppressFilter, loadmodule


@dataclass
class Config:
    server: settings.Server

    general: settings.General

    database: settings.database.Database

    integrations: settings.integrations.Integrations


@contextlib.asynccontextmanager
async def lifespan(application: FastAPI) -> None:
    """
    ASGI lifespan context for startup/shutdown events.
    """
    suppressor = LineSuppressFilter()

    config = application.state.config

    # allow arbitrary background tasks
    tasks = application.state.tasks = Tasks()

    try:
        config: Config = application.state.config

        if not isinstance(config, Config):
            required, actual = Config.__qualname__, type(config).__qualname__
            message = f"server config must be of {required} type, not {actual}"
            raise TypeError(message)

        # load database
        await loadmodule("database", __package__.rsplit(".", 1)[0], config.database)

        # create OpenAI client
        application.state.openai = OpenAI(api_key=config.general.token.get_secret_value())

        # load endpoints
        application.include_router((await loadmodule("endpoints", __package__, application)).router)

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


def factory(config: Config) -> FastAPI:
    root = FastAPI(
        lifespan=lifespan,
        title=outlines.metadata["Name"],
        description=outlines.metadata["Summary"],
    )

    # load enabled integrations
    if config.integrations.dummy.enabled:
        root = integrations.dummy(root, "/integrations/dummy")

    return root


logger = logging.getLogger(__name__)
