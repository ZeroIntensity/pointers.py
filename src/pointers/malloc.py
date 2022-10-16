import sys
from typing import Any, Optional, TypeVar

from ._cstd import c_free, c_malloc, c_realloc
from .base_pointers import BaseAllocatedPointer, IterDereferencable
from .exceptions import AllocationError, InvalidSizeError
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
        self._tracked = False

    @property
    def address(self) -> Optional[int]:
        return self._address

    @address.setter
    def address(self, value: int) -> None:
        self._address = value

    def __repr__(self) -> str:
        return f"AllocatedPointer(address={self.address}, size={self.size})"

    def __add__(self, amount: int):
        return AllocatedPointer(
            self.ensure() + amount,
            self.size,
            self.assigned,
        )

    def __sub__(self, amount: int):
        return AllocatedPointer(
            self.ensure() - amount,
            self.size,
            self.assigned,
        )

    @handle
    def free(self) -> None:
        self.ensure_valid()
        c_free(self.make_ct_pointer())
        self.freed = True


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
