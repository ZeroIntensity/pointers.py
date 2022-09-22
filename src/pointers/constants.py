import ctypes
from typing import Any, NamedTuple, Type, TypeVar, Union

__all__ = (
    "NULL",
    "Nullable",
    "raw_type",
)

T = TypeVar("T")


class NULL:
    """Unique object representing a NULL address."""


Nullable = Union[T, Type[NULL]]


class RawType(NamedTuple):
    tp: Type["ctypes._CData"]


def raw_type(ct: Type["ctypes._CData"]) -> Any:
    """Set a raw ctypes type for a struct."""
    return RawType(ct)
