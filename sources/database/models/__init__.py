from beanie import Document

from .claim import CLAIM
from .result import RESULT
from .document import DOCUMENT


__all__: tuple[str] = (
    "CLAIM",
    "RESULT",
    "DOCUMENT",
)


def all() -> tuple[type[Document]]:  # noqa: A001
    return tuple(model for name in __all__ if issubclass((model := globals()[name]), Document))
