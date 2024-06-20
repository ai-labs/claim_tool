"""
Versionable collections schema definition.
"""

import functools

from typing import ClassVar

from pydantic import BaseModel


__all__: tuple[str] = ("Schema",)


class Schema(type(BaseModel)):
    """
    Metaclass for custom versionable schemas.

    Contains all defined object schema versions.

    Examples
    --------
    >>> from beanie import Document
    >>> class Collection(Document, metaclass=Schema):
    ...     class Settings:
    ...         name = "accounts"
    ...         validate_on_save = True
    ...
    >>> class ACCOUNT(Collection, version=1):
    ...     username: str = "john.doe"
    ...     password: str = "drowssap"
    ...
    ... class ACCOUNT(ACCOUNT, version=2):
    ...     email: str
    ...     password: str
    ...
    >>> class ACCOUNT(Collection, version=2):
    ...     email: str
    ...     oauth: str

    """

    __refs__: ClassVar[set] = set()

    __version__: int

    __versions__: dict[int, type]

    @functools.wraps(type(BaseModel).__new__)
    def __new__(
        cls,
        *args,
        version: int | None = None,
        **kwargs,
    ) -> type:
        new = super().__new__(cls, *args, **kwargs)

        schema = ".".join([new.__module__, new.__qualname__])

        new.__version__ = version or 0

        if version is None or version == 0:
            new.__versions__ = {0: new}

        elif not hasattr(new, "__versions__"):
            message = f"{schema}: base is not defined"
            raise ValueError(message)

        elif max(new.__versions__) + 1 == version:
            new.__versions__[version] = new

        else:
            message = f"{schema}: invalid versions order"
            raise ValueError(message)

        cls.__refs__.add(new)

        return new

    @functools.wraps(type(BaseModel).__init__)
    def __init__(
        cls,
        name,
        bases,
        namespace,
        # **kwargs,
    ) -> None:
        super().__init__(name, bases, namespace)

    def __getitem__(cls, key: int) -> type:
        return cls.__versions__[key]

    def __repr__(cls) -> str:
        template = "<class '{}.{}' version={}>"
        return template.format(cls.__module__, cls.__qualname__, cls.__version__)

    @classmethod
    def models(cls) -> list[type]:
        """
        Get list of all defined versionable collections.

        Returns
        -------
        list[type]
            List of the latest versions of all schemas for database initialization.

        """
        return [model.__versions__[max(model.__versions__)] for model in cls.__refs__ if model.__version__ == 0]
