from __future__ import annotations

import importlib

from enum import Enum
from typing import Literal
from pathlib import Path

from pydantic import Field, BaseModel, ImportString, ValidationInfo, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    PydanticBaseSettingsSource,
)

from . import outlines


class TableTomlConfigSettingsSource(TomlConfigSettingsSource):
    """
    A source class that loads variables from a JSON file with table support.
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        toml_file: Path | None = None,
    ) -> None:
        self.toml_file_path = toml_file or settings_cls.model_config.get("toml_file")

        self.toml_table_header: tuple[str, ...] = settings_cls.model_config.get("toml_table_header", ())
        self.toml_data = self._read_files(self.toml_file_path)
        for key in self.toml_table_header:
            self.toml_data = self.toml_data.get(key, {})
        super(TomlConfigSettingsSource, self).__init__(settings_cls, self.toml_data)


class Settings(
    BaseSettings,
    validate_assignment=True,
    case_sensitive=True,
    extra="ignore",
):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        **sources: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (*sources.values(), TableTomlConfigSettingsSource(settings_cls))


class LOGLEVEL(str, Enum):
    """
    Valid logging levels.
    """

    CRITICAL: str = "CRITICAL"
    ERROR: str = "ERROR"
    WARNING: str = "WARNING"
    INFO: str = "INFO"
    DEBUG: str = "DEBUG"


class Formatter(BaseModel, extra="allow"):
    """
    Logging formatter.
    """

    type: ImportString = Field(None, alias="class")

    style: Literal["{", "%"] = None

    messages: str = None

    datetime: str = None

    check: bool = Field(None, alias="validate")


class Handler(BaseModel, extra="allow"):
    """
    Logging handler.
    """

    type: ImportString = Field(alias="class")

    level: LOGLEVEL = None

    formatter: str = None

    filters: list[str] = None


class Logger(BaseModel):
    """
    Logger configuration.
    """

    level: LOGLEVEL = None

    propagate: bool = None

    filters: list[str] = None

    handlers: list[str] = None


class Logging(Settings):
    """
    Logging system configuration.
    """

    model_config = SettingsConfigDict(toml_table_header=("logging",))

    level: LOGLEVEL = LOGLEVEL.INFO

    formatters: dict[str, Formatter] = {
        "default": Formatter.model_validate(
            {
                "style": "{",
                "messages": "{message}",
                "datetime": "%Y-%m-%d %H:%M:%S",
            }
        ),
    }

    handlers: dict[str, Handler] = {
        "default": Handler.model_validate(
            {
                "class": "rich.logging:RichHandler",
                "formatter": "default",
                "rich_tracebacks": True,
                "tracebacks_show_locals": False,
                "show_time": not outlines.journald,
                "show_path": not outlines.journald,
            }
        ),
    }

    loggers: dict[str, Logger] = {}

    @field_validator("formatters", "handlers", "loggers", mode="before")
    @classmethod
    def extend_default(cls, value: dict, info: ValidationInfo) -> dict:
        """
        Ensures that default items are preserved in collection.
        """
        return cls.model_fields[info.field_name].default | value

    def config(self) -> dict:
        """
        Generate dict suitable for `logging.dictConfig`.
        """

        self.prepare()

        output = {
            "version": 1,
            # "disable_existing_loggers": True,
            "formatters": {},
            "handlers": {},
            "loggers": {},
            "root": {},
        }

        # prepare formatters

        for name, item in self.formatters.items():
            result, extra = {}, item.dict(by_alias=True)

            if item.type is not None:
                result["()"] = f"{item.type.__module__}.{item.type.__name__}"
            del extra["class"]

            if item.messages is not None:
                result["format"] = item.messages
            del extra["messages"]

            if item.datetime is not None:
                result["datefmt"] = item.datetime
            del extra["datetime"]

            if item.style is not None:
                result["style"] = item.style
            del extra["style"]

            if item.check is not None:
                result["validate"] = item.check
            del extra["validate"]

            if extra:
                result.update(extra)

            if result:
                output["formatters"][name] = result

        # prepare handlers

        for name, item in self.handlers.items():
            result, extra = {}, item.dict(by_alias=True)

            result["class"] = f"{item.type.__module__}.{item.type.__name__}"

            del extra["class"]

            if item.level is not None:
                result["level"] = item.level.value
            del extra["level"]

            if item.formatter is not None:
                result["formatter"] = item.formatter
            del extra["formatter"]

            if item.filters is not None:
                result["filters"] = item.filters
            del extra["filters"]

            if extra:
                result.update(extra)

            if result:
                output["handlers"][name] = result

        # prepare loggers

        for name, item in self.loggers.items():
            result = {}

            if item.level is not None:
                result["level"] = item.level.value

            if item.propagate is not None:
                result["propagate"] = item.propagate

            if item.filters is not None:
                result["filters"] = item.filters

            if item.handlers is not None:
                result["handlers"] = item.handlers

            if result:
                output["loggers"][name] = result

        output["root"] = {"level": self.level.value, "handlers": ["default"]}

        return output

    def prepare(self) -> None:
        """
        Callback for logging machinery custom configuration.
        """


# import logging settings of the main package, if any
Logging = getattr(importlib.import_module(".settings", outlines.package), "Logging", Logging)
