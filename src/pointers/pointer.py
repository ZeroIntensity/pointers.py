import ctypes
from typing import (
    Generic,
    TypeVar,
    Any,
    Type,
    Iterator,
    Union,
)

from typing_extensions import ParamSpec
from contextlib import suppress
import faulthandler
from io import UnsupportedOperation
import sys

with suppress(
    UnsupportedOperation
):  # in case its running in idle or something like that
    faulthandler.enable()

__all__ = ("dereference_address", "Pointer", "to_ptr")

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

        deref_a: T = ~data
        deref_b: T = ~self

        size_a: int = sys.getsizeof(deref_a)
        size_b: int = sys.getsizeof(deref_b)

        if not size_a == size_b:
            raise MemoryError(
                f"object is of size {size_a}, while memory allocation is {size_b}"  # noqa
            )

        bytes_a = (ctypes.c_ubyte * sys.getsizeof(deref_a)) \
            .from_address(data.address)
        bytes_b = (ctypes.c_ubyte * sys.getsizeof(deref_b)) \
            .from_address(self.address)

        ctypes.memmove(bytes_b, bytes_a, len(bytes_a))

    def __lshift__(self, data: Union["Pointer[T]", T]):
        """Move data from another pointer to this pointer. Very dangerous, use with caution."""  # noqa
        self.move(data if isinstance(data, Pointer) else to_ptr(data))
        return self

    def __add__(self, amount: int):
        return Pointer(self.address + amount, self.type)

    def __sub__(self, amount: int):
        return Pointer(self.address - amount, self.type)


def to_ptr(val: T) -> Pointer[T]:
    """Convert a value to a pointer."""
    return Pointer(id(val), type(val))
