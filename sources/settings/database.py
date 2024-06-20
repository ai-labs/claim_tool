from typing import Annotated
from datetime import timedelta

from pydantic import Secret, PlainSerializer

from ailabs.claims.vendor.settings import (
    Settings,
    SettingsConfigDict,
)


class Database(Settings):
    model_config = SettingsConfigDict(toml_table_header=("database",))

    host: str = "localhost"

    port: int = 27017

    name: str = ...

    username: Secret[str] = ...

    password: Secret[str] = ...

    timeout: Annotated[
        timedelta,
        PlainSerializer(lambda item: item.total_seconds(), return_type=float),
    ] = timedelta(seconds=5.0)
