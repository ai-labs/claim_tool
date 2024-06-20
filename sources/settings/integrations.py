from pydantic import BaseModel

from ailabs.claims.vendor.settings import (
    Settings,
    SettingsConfigDict,
)


class Dummy(BaseModel):
    enabled: bool = False


class Integrations(Settings):
    model_config = SettingsConfigDict(toml_table_header=("integrations",))

    dummy: Dummy = Dummy()
