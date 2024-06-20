import queue
import asyncio
import logging
import importlib

from types import ModuleType
from typing import Awaitable


class LineSuppressFilter(logging.Filter):
    """
    After added to the logger, suppress one line and remove itself from it.
    """

    def filter(self, record) -> bool:
        logger = logging.getLogger(record.name)
        logger.removeFilter(self)
        return False


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


async def loadmodule(name: str, package: str, /, *args, **kwargs) -> ModuleType:
    try:
        if hasattr((module := importlib.import_module(f".{name}", package)), "initialize"):
            await module.initialize(*args, **kwargs)
        return module
    except Exception as error:
        logger.error("Failed to load module: %s", name, exc_info=error)
        raise asyncio.CancelledError from error


logger = logging.getLogger(__name__)
