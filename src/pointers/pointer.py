import ctypes
from typing import (
    Generic,
    TypeVar,
    Any,
    Type,
    get_type_hints,
    Callable,
    Iterator,
    Union,
)

from typing_extensions import ParamSpec
import inspect
from functools import wraps
from contextlib import suppress
import faulthandler
from io import UnsupportedOperation
import sys

with suppress(
    UnsupportedOperation
):  # in case its running in idle or something like that
    faulthandler.enable()

__all__ = ("dereference_address", "Pointer", "to_ptr", "decay")

T = TypeVar("T")
A = TypeVar("A")
P = ParamSpec("P")


def dereference_address(address: int) -> Any:
    """Dereference an address. Will cause a segmentation fault if the address is invalid."""  # noqa
    return ctypes.cast(address, ctypes.py_object).value


class Pointer(Generic[T]):
    """Base class representing a pointer."""

    def __init__(self, address: int, typ: Type[T]) -> None:
        self._address = address
        self._type = typ

    @property
    def address(self) -> int:
        """Address of the pointer."""
        return self._address

    @property
    def type(self) -> Type[T]:
        """Type of the pointer."""
        return self._type

    def __repr__(self) -> str:
        return (
            f"<pointer to {self.type.__name__} object at {hex(self.address)}>"  # noqa
        )

    def __str__(self) -> str:
        return hex(self.address)

    def dereference(self) -> T:
        """Dereference the pointer."""
        return dereference_address(self.address)

    def __iter__(self) -> Iterator[T]:
        """Dereference the pointer."""
        return iter({self.dereference()})

    def __invert__(self) -> T:
        """Dereference the pointer."""
        return self.dereference()

    def assign(self, new: "Pointer[T]") -> None:
        """Point to a different address."""
        if new.type is not self.type:
            raise ValueError("new pointer must be the same type")

        self._address = new.address

    def __rshift__(self, value: Union["Pointer[T]", T]):
        """Point to a different address."""
        self.assign(value if isinstance(value, Pointer) else to_ptr(value))
        return self

    def move(self, data: "Pointer[T]") -> None:
        """Move data from another pointer to this pointer. Very dangerous, use with caution."""  # noqa
        if data.type is not self.type:
            raise ValueError("pointer must be the same type")

        bytes_a = (ctypes.c_ubyte * sys.getsizeof(~data)) \
            .from_address(data.address)
        bytes_b = (ctypes.c_ubyte * sys.getsizeof(~self)) \
            .from_address(self.address)

        ctypes.memmove(bytes_b, bytes_a, len(bytes_a))

    def __lshift__(self, data: Union["Pointer[T]", T]):
        """Move data from another pointer to this pointer. Very dangerous, use with caution."""  # noqa
        self.move(data if isinstance(data, Pointer) else to_ptr(data))
        return self

    def __add__(self, amount: int):
        self._address += amount
        return self

    def __sub__(self, amount: int):
        self._address -= amount
        return self


def to_ptr(val: T) -> Pointer[T]:
    """Convert a value to a pointer."""
    return Pointer(id(val), type(val))


def decay(func: Callable[P, T]) -> Callable[..., T]:
    """Automatically convert values to pointers when called."""

    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        hints = get_type_hints(func)
        actual: dict = {}
        params = inspect.signature(func).parameters

        # mypy is giving false positives here since it doesn't know how to
        # handle paramspec
        for index, key in enumerate(params):
            if key in kwargs:  # type: ignore
                actual[key] = kwargs[key]  # type: ignore
            else:
                with suppress(IndexError):
                    actual[params[key].name] = args[index]  # type: ignore

        for key, value in hints.items():
            if (hasattr(value, "__origin__")) and (value.__origin__ is Pointer): # noqa
                actual[key] = to_ptr(actual[key])

        return func(**actual)

    return inner
