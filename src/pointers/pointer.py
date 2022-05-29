import ctypes
from typing import (
    Generic,
    TypeVar,
    Type,
    Iterator,
    Union,
    Any
)

from typing_extensions import ParamSpec
from contextlib import suppress
import faulthandler
from io import UnsupportedOperation
import sys
import gc
from functools import lru_cache
from .exceptions import (DereferenceError,
                         IncorrectItemExpectedForSubscriptError,
                         NotSubscriptableError,
                         ImmutableObjectError)

__all__ = ("Pointer", "to_ptr", "dereference_address", "dereference_tracked")


def dereference_address(address: int) -> Any:
    """Get the PyObject at the given address."""
    return ctypes.cast(address, ctypes.py_object).value


def dereference_tracked(address: int) -> Any:
    """Dereference an object tracked by the garbage collector."""
    for obj in gc.get_objects():
        if id(obj) == address:
            return obj

    raise DereferenceError(
        f"address {hex(address)} does not exist (probably removed by the garbage collector)"  # noqa
    )


with suppress(
    UnsupportedOperation
):  # in case its running in idle or something like that
    faulthandler.enable()

T = TypeVar("T")
A = TypeVar("A")
P = ParamSpec("P")


class Pointer(Generic[T]):
    """Base class representing a pointer."""

    def __init__(self, address: int, typ: Type[T], tracked: bool) -> None:
        self._address = address
        self._type = typ
        self._tracked = tracked

    @property
    def tracked(self) -> bool:
        """Whether the pointed object is tracked by the garbage collector."""
        return self._tracked

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

    def __rich__(self):
        return f"<pointer to [green]{self.type.__name__}[/green] object at [cyan]{hex(self.address)}[/cyan]>"  # noqa

    def __str__(self) -> str:
        return hex(self.address)

    def dereference(self) -> T:
        """Dereference the pointer."""
        return (dereference_tracked if self.tracked else dereference_address)(self.address)  # noqa

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

        bytes_a = (ctypes.c_ubyte * sys.getsizeof(deref_a)) \
            .from_address(data.address)
        bytes_b = (ctypes.c_ubyte * sys.getsizeof(deref_b)) \
            .from_address(self.address)

        ctypes.memmove(bytes_b, bytes_a, len(bytes_a))

    def __lshift__(self, data: Union["Pointer[T]", T]):
        """Move data from another pointer to this pointer. Very dangerous, use with caution."""  # noqa
        self.move(data if isinstance(data, Pointer) else to_ptr(data))
        return self  # noqa


    def __getitem__(self, item):
        """Allows subscription to PyObject referenced Pointers. Inherited by Malloc,
           superceded for CallocPointers. Works with numpy, pandas, etc.

            x = np.arange(100).reshape(4, 25)
            v = to_ptr(x)

            >> v[(0, 4)]
            >> 3
           """  # noqa

        dereferenced = self.dereference()

        subscriptable = [type(Pointer), type(dict())]
        referencable = [type(tuple()), type(int()), type(str()), type(list())]

        if hasattr(dereferenced, '__getitem__'):
            return dereferenced[item]  # noqa

        elif hasattr(dereferenced, '__iter__'):
            if (type(item) in referencable) and (type(dereferenced) in subscriptable):
                return dereferenced[item]  # noqa

            else:
                raise IncorrectItemExpectedForSubscriptError("""Subscript with an Int,
                                        wrong item type for referenced PyObject.""")
        else:
            raise NotSubscriptableError("""Ensure PyObject types are correct for
                                        subscription prior to accessing the item.""")

    def __setitem__(self, item, replace):
        """Allows item assignment to PyObject referenced Pointers. Inherited by Malloc,
           superceded for CallocPointers. Works with numpy, pandas, etc.

            x = np.arange(100).reshape(4, 25)
            v = to_ptr(x)
            v[(0, 4)] = 2

            >> v[0]
            >> array([ 0,  1,  2,  3,  2,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
                   17, 18, 19, 20, 21, 22, 23, 24])
            >> x[0]
            >> array([ 0,  1,  2,  3,  2,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
                   17, 18, 19, 20, 21, 22, 23, 24])
        """  # noqa

        dereferenced = self.dereference()

        if hasattr(dereferenced, '__setitem__'):
            dereferenced[item] = replace  # noqa
        else:
            raise ImmutableObjectError("""PyObject does not support item assignment.
                                          Ensure PyObject type is correct for the pointer
                                          you are accessing.""")


def to_ptr(val: T) -> Pointer[T]:
    """Convert a value to a pointer."""
    return Pointer(id(val), type(val), gc.is_tracked(val))
