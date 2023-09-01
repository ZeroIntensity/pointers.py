from __future__ import annotations

import ctypes
from typing import Any, Callable, TypeVar

from _pointers import SegvError, handle
from typing_extensions import ParamSpec

from .exceptions import SegmentationFault

__all__ = (
    "NULL",
    "Nullable",
    "address_of",
    "inc_ref_obj",
    "dec_ref_obj",
    "memory_handler",
)

T = TypeVar("T")
P = ParamSpec("P")


class NULL:
    """Sentinel value for a NULL."""


Nullable = T | type[NULL]


def address_of(obj: Nullable[Any]) -> int:
    """Get the address of an object, or 0 if NULL.

        Example:
            ```py
    from pointers import address_of, NULL

    print(address_of(NULL))  # 0
            ```"""
    if obj is NULL:
        return 0

    return id(obj)


def inc_ref_obj(obj: object) -> None:
    """Increment the reference count on an object."""
    ctypes.pythonapi.Py_IncRef(obj)


def dec_ref_obj(obj: object) -> None:
    """Decrement the reference count on an object."""
    ctypes.pythonapi.Py_DecRef(obj)


def memory_handler(func: Callable[P, T]) -> Callable[P, T]:
    """Handle memory errors inside of a function.

    Example:
        ```py
    from pointers import memory_handler


    @memory_handler
    def hello():
        ctypes.string_at(0)


    hello()
    ```
    """

    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return handle(func, args, kwargs)
        except SegvError as e:
            raise SegmentationFault(str(e)) from None

    return inner
