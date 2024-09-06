from abc import ABC, abstractmethod
from typing import Generic, TypeVar, final

from _pointers import decref, deref, incref

__all__ = "Pointer", "PyObjectPointer"

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
        ...

    @final
    def __not__(self) -> T:
        return self.dereference()

class PyObjectPointer(Pointer[T], Generic[T]):
    """
    Type representing a pointer to a Python object.
    """
    def __init__(self, address: int) -> None:
        self.address = address
        self.refcount += 1

    def dereference(self) -> T:
        ...

    @property
    def refcount(self) -> int:
        """
        The reference count of the underlying object.
        """
        return 0

    @refcount.setter
    def refcount(self, value: int) -> None:
        pass

    def immortalize(self) -> None:
        """
        Turn the underlying object into a PEP 683 immortal object.

        On <3.12, this method raises a `CompatibilityError`.
        """
        ...

    def defer_refcount(self) -> None:
        """
        Enable PEP 703 deferred reference counting on the object.

        If this is called on a build with the GIL enabled, this
        raises a `CompatibilityError`.
        """
