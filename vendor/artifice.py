"""
Essential types and functions for better CLI experience.
"""

import inspect
import logging
import contextlib

from types import FrameType, TracebackType
from typing import Callable

import rich

from rich import text, pretty
from typer import BadParameter
from rich.console import Console
from click.exceptions import ClickException


class ColoredBadParameter(BadParameter):
    """
    Click exception with rich support in error panel.

    Renders colored traceback of original exception, if any.

    Behaves as parent if is not a direct consequence of another exception.
    """

    def format_message(self) -> str:
        if not self.message:
            self.message = ""

        # get original exception

        error: BaseException | None = None

        if isinstance(self.__cause__, BaseException):
            error = self.__cause__.__cause__ or self.__cause__

        if error is None:
            return super().format_message()

        # get renderable for original exception

        console = pretty.get_console()

        message = error.with_traceback(None)

        with console:
            # WARNING: we need to construct renderable by ourselves
            renderables = console._collect_renderables([message], " ", "\n")
            for hook in console._render_hooks[:]:
                renderables = hook.process_renderables(renderables)
            renderable = renderables[0]

        # get original format for empty message

        message = self.message

        super().__init__("")

        base = text.Text(super().format_message())

        self.message = message

        # extend original message with colored error render

        base.append(renderable)

        return base


@contextlib.contextmanager
def clickerize(
    newtype: ClickException | None = None,
    *,
    console: Console | None = None,
) -> None:
    """
    Handle any exception as a given ClickException subclass.

    Exception type convertion is done like this:

    ClickException subtype -> newtype if given, otherwise keep current
    BaseException -> newtype if given, otherwise ClickException

    For non-click exceptions traceback is stripped out.

    For all exceptions messages are rendered with rich.

    Parameters
    ----------
    newtype : ClickException, optional
        What new exception type should be used.
    console : Console, optional
        Explicit Console instalnce used to render messages.
    """

    def substitute(newtype, *objects) -> ClickException:
        nonlocal console

        if console is None:
            console = rich.pretty.get_console()

        renderables = console._collect_renderables(objects, " ", "\n")
        for hook in console._render_hooks[:]:
            renderables = hook.process_renderables(renderables)
        renderable = renderables[0]

        text = rich.text.Text(newtype("").format_message())
        text.append(renderable)

        error = newtype(renderable)
        error.format_message = lambda: text

        return error

    caller = inspect.getmodule(inspect.stack()[2][0])  # 1 is contextlib, 2 - actual caller
    logger = logging.getLogger(caller.__name__)

    try:
        yield
    except ClickException as error:
        logger.debug("unhandled exception raised under wrapper", exc_info=error.__cause__)
        # pretty print messages of click exceptions
        message = error.message

        if newtype is None:
            newtype = type(error)

        raise substitute(newtype, message) from error

    except BaseException as error:
        logger.debug("unhandled exception raised under wrapper", exc_info=error)
        # pretty print generic exceptions
        message = error.with_traceback(None)

        if newtype is None:
            newtype = ClickException

        raise substitute(newtype, message) from error


def getshowwarning(*, showstack: bool) -> Callable:
    """
    Makes custom warning.showwarning function that logs warnings with optional traceback.
    """

    def showwarning(
        message,
        category,
        filename,
        lineno,
        file=None,  # noqa: ARG001
        line=None,  # noqa: ARG001
    ) -> str:
        logger = logging.getLogger(__name__)

        # get stack

        stack: list[FrameType] = []

        if (frame := inspect.currentframe()) is not None:
            # use the faster inspect.currentframe where implemented
            while frame is not None:
                stack.append(frame)

                frame = frame.f_back

        else:
            # fallback to the slower inspect.stack
            stack = [info.frame for info in inspect.stack()]

        # ignore frames from this helper and warnings module

        stack = stack[2:]

        if showstack:
            # get traceback

            traceback: TracebackType = None

            for frame in stack:
                traceback = TracebackType(traceback, frame, frame.f_lasti, frame.f_lineno)

            exc_info = (category, message, traceback)

        else:
            exc_info = False

        message = logging.LogRecord(
            logger.name,
            logging.WARNING,
            filename,
            lineno,
            message,
            (),
            exc_info=exc_info,
        )

        logger.handle(message)

    return showwarning
