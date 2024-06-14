"""
Current runtime description.
"""

import os
import sys
import functools
import importlib.metadata

from .. import __package__ as package  # noqa: TID252


__all__: tuple[str] = ("package", "namespace", "metadata", "journald")


@functools.lru_cache
def isjournald() -> bool:
    """
    Check if journald is listening on stderr.
    """
    if (stream := os.getenv("JOURNAL_STREAM", None)) is None:
        return False

    st_dev, st_ino = map(int, stream.split(":", 1))

    stat = os.stat(sys.stderr.fileno())

    return stat.st_ino == st_ino and stat.st_dev == st_dev


# pylint: disable=invalid-name

# namespace name if any
namespace = ".".join(package.split(".")[:-1])

# package distribution
distribution = importlib.metadata.distribution(package)

# distribution metadata
metadata = distribution.metadata

# is journald listenong on stderr
journald = isjournald()
