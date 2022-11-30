import ctypes
import faulthandler
from contextlib import suppress
from functools import wraps
from io import UnsupportedOperation
from typing import (
    TYPE_CHECKING, Any, Callable, NamedTuple, Type, TypeVar, Union
)

from typing_extensions import ParamSpec

from _pointers import handle as _handle

from .exceptions import SegmentViolation

if TYPE_CHECKING:
    from .structure import Struct, StructPointer

with suppress(
    UnsupportedOperation
):  # in case its running in idle or something like that
    faulthandler.enable()

__all__ = (
    "NULL",
    "Nullable",
    "raw_type",
    "handle",
    "struct_cast",
)

T = TypeVar("T")
P = ParamSpec("P")


class NULL:
    """Unique object representing a NULL address.

    May be used with object pointers or passed to bindings.
    """


Nullable = Union[T, Type[NULL]]


class RawType(NamedTuple):
    tp: Type["ctypes._CData"]


def raw_type(ct: Type["ctypes._CData"]) -> Any:
    """Set a raw ctypes type for a struct."""
    return RawType(ct)


def handle(func: Callable[P, T]) -> Callable[P, T]:
    """Handle segment violation errors when called."""

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

            if not any(
                {
                    msg.startswith("segment violation"),
                    msg.startswith("exception: access violation"),
                }
            ):
                raise

            with suppress(UnsupportedOperation):
                faulthandler.enable()

            raise SegmentViolation(msg) from None

    return wrapper


@handle
def struct_cast(ptr: Union["Struct", "StructPointer"]) -> Any:
    """Cast a `Struct` or `StructPointer` to a Python object."""
    return ctypes.cast(ptr.get_existing_address(), ctypes.py_object).value
