import os
import sys
import logging
import pkgutil
import warnings
import importlib
import logging.config

from types import TracebackType
from typing import Optional, Annotated
from pathlib import Path

import tomlkit

from typer import Exit, Typer, Option, Context, launch
from click.exceptions import FileError, BadParameter, ClickException
from typer.rich_utils import rich_format_error

from . import artifice, basedirs, outlines, settings


application = Typer(rich_markup_mode="rich")


# import commands of the main package
commands = importlib.import_module(".commands", outlines.package)

for info in pkgutil.iter_modules(commands.__path__):
    module = importlib.import_module(f".{info.name}", commands.__package__)

    if isinstance(command := getattr(module, "application", None), Typer):
        application.add_typer(command)


def setconfig(context: Context, value: Path) -> basedirs.Directories:
    """
    Adjust default config path relative to the appdir. Ensure appdir exists.
    """
    try:
        dirs = basedirs.Directories(
            outlines.package.replace(".", os.path.sep) if not value else None,
            root=value,
        )
    except FileExistsError as error:
        message = f"{value} is not a directory"
        raise BadParameter(message) from error
    except PermissionError as error:
        raise BadParameter(error.strerror) from error

    config = next(filter(lambda item: item.name == "config", context.command.params))

    config.default = dirs.config / config.default

    return dirs


@application.callback(
    help=outlines.metadata["Summary"],
    invoke_without_command=True,
    no_args_is_help=True,
)
def callback(
    context: Context,
    appdir: Annotated[
        Path | basedirs.Directories,
        Option(
            "--appdir",
            path_type=Path,
            resolve_path=True,
            callback=setconfig,
            help="Directory for configuration and runtime data.",
            show_default="XDG Base Directories",
        ),
    ] = None,
    config: Annotated[
        Path,
        Option(
            "--config",
            path_type=Path,
            resolve_path=True,
            help="Configuration file path. Default value is relative to appdir.",
        ),
    ] = Path("config.toml"),
    edit: Annotated[
        Optional[bool],
        Option(
            "--edit-config",
            help="Open config file in default editor and exit.",
        ),
    ] = None,
    verbose: Annotated[
        int,
        Option(
            "-v",
            "--verbose",
            count=True,
            show_default=False,
            help="Gradually increase logging level. Relative to config value.",
        ),
    ] = 0,
) -> None:
    context.obj = {"appdir": appdir}

    if edit:
        if not config.exists():
            # generate config file

            stack: list[type[settings.Settings]] = [*settings.Settings.__subclasses__()]

            data: dict[str, ...] = {}

            while stack:
                stack.extend((item := stack.pop()).__subclasses__())

                # dump default config

                section = ".".join(item.model_config.get("toml_table_header", [item.__name__.lower()])) or None

                item = item.model_construct().model_dump(mode="json", by_alias=True, exclude_none=True)

                if section is not None:
                    if section in data:
                        data[section].update(item)
                    else:
                        data[section] = item

                else:
                    data.update(item)

            try:
                with config.open("wt", encoding="utf-8") as buffer:
                    tomlkit.dump(data, buffer)
            except PermissionError as error:
                raise FileError(config, error.strerror) from error

        raise Exit(launch(str(config), wait=True))

    if config.is_file():
        # set config path for all child settings models

        stack: list[type[settings.Settings]] = [settings.Settings]

        while stack:
            item = stack.pop()
            item.model_config["toml_file"] = config
            stack.extend(item.__subclasses__())

    with artifice.clickerize(BadParameter):
        # configure logging

        try:
            levelsmap = logging.getLevelNamesMapping
        except AttributeError:
            # python 3.10; pylint: disable=protected-access
            levelsmap = logging._nameToLevel.copy

        levelsmap = levelsmap()

        data = settings.Logging()

        data.level = logging.getLevelName(max(levelsmap[data.level] - (verbose * 10), 10))

        logging.config.dictConfig(data.config())

        # WARNING: do not use logging until this point

        # allow warnings to be logged

        warnings.showwarning = artifice.getshowwarning(showstack=levelsmap[data.level] <= logging.DEBUG)

        # WARNING: do not use warnings until this point

    # log and suppress uncaught exceptions traceback

    def excepthook(exception: type[BaseException], value: BaseException, traceback: TracebackType | None) -> None:
        logger = logging.getLogger()

        logger.critical(
            "unhandled exception caught",
            exc_info=(exception, value, traceback),
        )

        message = "Application finished with an error. See logs for more info."

        value = ClickException(message)

        return rich_format_error(value)

    sys.excepthook = excepthook
