import importlib

from typing import Annotated

from pydantic import Field, Secret

from ailabs.claims.vendor.settings import (
    LOGLEVEL,
    Logger,
    Handler,
    Logging,
    Settings,
    Formatter,
    SettingsConfigDict,
    outlines,
)


class Server(Settings):
    model_config = SettingsConfigDict(toml_table_header=("server",))

    host: str = "127.0.0.1"

    port: int = 8000


class General(Settings):
    model_config = SettingsConfigDict(toml_table_header=("general",))

    interval: float = 10.0

    threshold: float = 100.0

    token: Annotated[
        Secret[str],
        Field(description="OpenAI API token."),
    ]


class Logging(Logging):
    formatters: dict[str, Formatter] = {  # noqa: RUF012
        "default": Formatter.model_validate(
            {
                "style": "{",
                "messages": "{message}",
                "datetime": "%Y-%m-%d %H:%M:%S",
            }
        ),
        "access": Formatter.model_validate(
            {
                "class": "uvicorn.logging.AccessFormatter",
                "style": "{",
                "messages": "{client_addr} {status_code} - {request_line}",
                "datetime": "%Y-%m-%d %H:%M:%S",
                "use_colors": False,
            }
        ),
    }

    handlers: dict[str, Handler] = {  # noqa: RUF012
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
        "access": Handler.model_validate(
            {
                "class": "rich.logging:RichHandler",
                "formatter": "access",
                "rich_tracebacks": True,
                "tracebacks_show_locals": False,
                "show_time": not outlines.journald,
                "show_path": not outlines.journald,
            }
        ),
    }

    loggers: dict[str, Logger] = {  # noqa: RUF012
        "uvicorn": Logger.model_validate(
            {
                "propagate": False,
                "handlers": ["default"],
            }
        ),
        "uvicorn.error": Logger.model_validate(
            {
                "propagate": False,
                "handlers": ["default"],
            }
        ),
        "uvicorn.access": Logger.model_validate(
            {
                "level": LOGLEVEL.INFO,
                "propagate": False,
                "handlers": ["access"],
            }
        ),
    }


database = importlib.import_module(".database", __package__)
