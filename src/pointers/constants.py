import ctypes
import faulthandler
from contextlib import suppress
from functools import wraps
from io import UnsupportedOperation
from typing import Any, Callable, NamedTuple, Type, TypeVar, Union

from typing_extensions import ParamSpec

from _pointers import handle as _handle

from .exceptions import Aborted, SegmentViolation

with suppress(
    UnsupportedOperation
):  # in case its running in idle or something like that
    faulthandler.enable()

__all__ = (
    "NULL",
    "Nullable",
    "raw_type",
    "handle",
)

T = TypeVar("T")
P = ParamSpec("P")


class NULL:
    """Unique object representing a NULL address."""


Nullable = Union[T, Type[NULL]]


class RawType(NamedTuple):
    tp: Type["ctypes._CData"]


def raw_type(ct: Type["ctypes._CData"]) -> Any:
    """Set a raw ctypes type for a struct."""
    return RawType(ct)


def handle(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            faulthandler.disable()
            call = _handle(func, args, kwargs)

            with suppress(UnsupportedOperation):
                faulthandler.enable()

            return call
        except (RuntimeError, OSError) as e:
            msg = str(e)
            segv = any(
                {
                    msg.startswith("segment violation"),
                    msg.startswith("exception: access violation"),
                }
            )

            aborted = msg.startswith(
                "python aborted",
            )

            if (not segv) and (not aborted):
                raise

            with suppress(UnsupportedOperation):
                faulthandler.enable()

            raise (SegmentViolation if segv else Aborted)(str(e)) from None

    return wrapper
