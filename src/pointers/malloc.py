from __future__ import annotations
import sys
from typing import Any, Optional, TypeVar

from ._cstd import c_free, c_malloc, c_realloc
from .base_pointers import BaseAllocatedPointer, IterDereferencable
from .exceptions import AllocationError, InvalidSizeError
from .stack_pointer import StackAllocatedPointer
from .util import handle

__all__ = ("AllocatedPointer", "malloc", "free", "realloc")


T = TypeVar("T")
A = TypeVar("A", bound=BaseAllocatedPointer)


class AllocatedPointer(IterDereferencable[T], BaseAllocatedPointer[T]):
    """Pointer to allocated memory."""

    def __init__(
        self,
        address: int,
        size: int,
        assigned: bool = False,
        parent: AllocatedPointer[T] | None = None
    ) -> None:
        """
        Args:
            address: Address of the allocated memory.
            size: Size of the allocated memory.
            assigned: Whether an object is currently inside the memory.
        """
        self._address = address
        self._size = size
        self._freed = False
        self._assigned = assigned
        self._parent: AllocatedPointer[T] | None = parent

    def _indexed(self, amount: int) -> AllocatedPointer[T]:
        return AllocatedPointer(
            self.ensure() + amount,
            self.size - amount,
            self.assigned,
            parent=self._parent,
        )

    def _get_parent(self) -> AllocatedPointer[T]:
        parent = self

        while parent._parent:
            parent = parent._parent

        return parent
    
    @property
    def freed(self) -> bool:
        return self._get_parent()._freed

    @freed.setter
    def freed(self, value: bool) -> None:
        self._get_parent()._freed = value

    @property
    def address(self) -> Optional[int]:
        return self._address

    @address.setter
    def address(self, value: int) -> None:
        self._address = value

    def __repr__(self) -> str:
        return f"AllocatedPointer(address={self.address}, size={self.size})"

    def __add__(self, amount: int) -> AllocatedPointer[T]:
        return self._indexed(amount)

    def __sub__(self, amount: int) -> AllocatedPointer[T]:
        return self._indexed(amount)

    @handle
    def free(self) -> None:
        self.ensure_valid()
        c_free(self.make_ct_pointer())
        self.freed = True

    @handle
    def __getitem__(self, index: int) -> AllocatedPointer[T]:
        if not isinstance(index, int):
            raise ValueError(f"memory indices must be int, not {type(index).__name__}")

        return self._indexed(index)

    @handle
    def __setitem__(self, index: int, value: T) -> None:
        if not isinstance(index, int):
            raise ValueError(f"memory indices must be int, not {type(index).__name__}")

        ptr = self._indexed(index)
        ptr <<= value


def malloc(size: int) -> AllocatedPointer[Any]:
    """Allocate memory of a given size.

    Args:
        size: Allocation size.

    Returns:
        Pointer to allocated memory.

    Raises:
        AllocationError: Raised when allocation fails, presumably due to no memory.

    Example:
        ```py
        ptr = malloc(1)
        ```
    """  # noqa
    mem = c_malloc(size)

    if not mem:
        raise AllocationError("failed to allocate memory")

    return AllocatedPointer(mem, size)


def free(target: BaseAllocatedPointer):
    """Equivalent to `target.free()`

    Args:
        target: Pointer to free.

    Example:
        ```py
        ptr = malloc(1)
        free(ptr)  # is the same as `ptr.free()`
        ```"""
    target.free()


@handle
def realloc(target: A, size: int) -> A:
    """Resize a memory block created by malloc.

    Args:
        target: Pointer to reallocate.
        size: New allocation size.

    Returns:
        Original object.

    Raises:
        InvalidSizeError: Object inside allocation is larger than attempted reallocation.
        AllocationError: Raised when allocation fails, presumably due to no memory.

    Example:
        ```py
        ptr = malloc(1)
        realloc(ptr, 2)
        ```
    """  # noqa
    if type(target) is StackAllocatedPointer:
        raise TypeError("pointers to items on the stack may not be resized")

    tsize: int = sys.getsizeof(~target)

    if target.assigned and (tsize > size):
        raise InvalidSizeError(
            f"object inside memory is of size {tsize}, so memory cannot be set to size {size}",  # noqa
        )

    addr = c_realloc(target.address, size)

    if not addr:
        raise AllocationError("failed to resize memory")

    target.size = size
    target.address = addr
    return target
