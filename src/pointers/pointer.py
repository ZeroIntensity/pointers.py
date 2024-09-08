from __future__ import annotations

import ctypes
import sys
import weakref
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, final

from typing_extensions import Self

from _pointers import decref, deref, getref, incref, setimmortal, setref

from .exceptions import BufferOverflowError, CompatibilityError

__all__ = "Pointer", "PyObjectPointer", "to_ptr", "BufferPointer"

T = TypeVar("T")


class Pointer(ABC, Generic[T]):
    """
    Base type used for all pointer objects.
    """

    address: int
    """Memory address that the object is pointing to."""

    @abstractmethod
    def dereference(self) -> T:
        """
        Dereference the pointer.
        """

    @final
    def __invert__(self) -> T:
        return self.dereference()

    @abstractmethod
    def move(self, src: Self, *, allow_overflow: bool = False) -> None:
        """
        Move the memory of `src` into this pointer.
        """

    @final
    def __ilshift__(self, src: Self):
        self.move(src)

    @final
    def __ixor__(self, src: Self):
        self.move(src, allow_overflow=True)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} to {hex(self.address)}>"

    __str__ = __repr__


class BufferPointer(Pointer[bytes]):
    def __init__(
        self,
        address: int,
        size: int | None = None,
    ) -> None:
        self.address = address
        self._size = size

    def dereference(self) -> bytes:
        if self._size is not None:
            return ctypes.string_at(self.address, size=self._size)
        return ctypes.string_at(self.address)

    def size(self):
        return len(~self) if self._size is None else self._size

    def _as_buffer(self) -> ctypes.Array[ctypes.c_ubyte]:
        return (ctypes.c_ubyte * self.size()).from_address(self.address)

    def move(
        self, src: BufferPointer, *, allow_overflow: bool = False
    ) -> None:
        src_size = src.size()
        self_size = self.size()

        if (src_size > self_size) and (not allow_overflow):
            raise BufferOverflowError(
                f"{src} will overflow {src_size - self_size} bytes"
            )

        ctypes.memmove(self._as_buffer(), src._as_buffer(), src_size)


class PyObjectPointer(Pointer[T], Generic[T]):
    """
    Type representing a pointer to a Python object.
    """

    def __init__(self, address: int) -> None:
        self.address = address
        self.refcount += 1
        weakref.finalize(self, self._cleanup)

    def _cleanup(self) -> None:
        self.refcount -= 1

    def size(self) -> int:
        return sys.getsizeof(~self)

    def dereference(self) -> T:
        return deref(self.address)

    @property
    def refcount(self) -> int:
        """
        The reference count of the underlying object.
        """
        return getref(~self)

    @refcount.setter
    def refcount(self, value: int) -> None:
        setref(~self, value + 1)

    def immortalize(self) -> None:
        """
        Turn the underlying object into a PEP 683 immortal object.

        On <3.12, this method raises a `CompatibilityError`.
        """
        if sys.version_info >= (3, 12):
            setimmortal(~self)
        else:
            raise CompatibilityError(
                "immortal objects are not supported on this version",
            )

    def defer_refcount(self) -> None:
        """
        Enable PEP 703 deferred reference counting on the object.

        If this is called on a build with the GIL enabled, this
        raises a `CompatibilityError`.
        """
        raise CompatibilityError(
            "deferred reference counting is not supported",
        )

    def as_buffer(self) -> BufferPointer:
        return BufferPointer(self.address, self.size())

    def move(self, src: Self, *, allow_overflow: bool = False) -> None:
        return self.as_buffer().move(
            src.as_buffer(), allow_overflow=allow_overflow,
        )


def to_ptr(obj: T) -> PyObjectPointer[T]:
    incref(obj)
    ptr = PyObjectPointer(id(obj))
    decref(obj)
    return ptr
