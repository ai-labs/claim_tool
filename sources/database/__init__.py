"""
Database connection, models and migrations.

Is a `database` entrypoint of the main package.

Should be initialized with `utilities.initialize`.
"""

import logging

from pathlib import Path

from beanie import init_beanie
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie.executors.migrate import MigrationSettings, run_migrate

from ailabs.claims.settings import database as settings

from . import models


__all__: tuple[str] = ("models",)


async def initialize(config: settings.Database) -> AsyncIOMotorDatabase:
    """
    Startup hook for database initialization and migrations.

    Any exception raised here will terminate server startup process.
    """
    client = AsyncIOMotorClient(
        config.host,
        config.port,
        tz_aware=True,
        username=config.username.get_secret_value(),
        password=config.password.get_secret_value(),
        serverSelectionTimeoutMS=int(config.timeout.total_seconds() * 1000),
    )

    try:
        client.admin.command("ping")
    except ConnectionFailure:
        logger.error("Failed to initialize database: server not available")

        logger.debug("Exact cause of failure:", exc_info=True)

        raise

    # pylint: disable=invalid-name

    database = client[config.name]

    try:
        await init_beanie(database, document_models=models.all())
    except ServerSelectionTimeoutError:
        logger.error("Failed to initialize database: timed out")

        logger.debug("Exact cause of failure:", exc_info=True)

        raise

    dsn: str = "mongodb://{username}:{password}@{host}:{port}"

    await run_migrate(
        MigrationSettings(
            direction="FORWARD",
            distance=0,
            connection_uri=dsn.format(
                username=config.username.get_secret_value(),
                password=config.password.get_secret_value(),
                host=config.host,
                port=config.port,
            ),
            database_name=config.name,
            allow_index_dropping=True,
            path=Path(__file__).with_name("migrations"),
        )
    )

    return client


logger = logging.getLogger(__name__)
