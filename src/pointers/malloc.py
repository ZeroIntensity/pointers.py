from typing import Any, Optional, TypeVar

from ._cstd import c_free, c_malloc, c_realloc
from ._pointer import BaseAllocatedPointer, IterDereferencable
from .exceptions import AllocationError

__all__ = ("AllocatedPointer", "malloc", "free", "realloc")


T = TypeVar("T")
A = TypeVar("A", bound=BaseAllocatedPointer)


class AllocatedPointer(IterDereferencable[T], BaseAllocatedPointer[T]):
    """Class representing a pointer created by malloc."""

    def __init__(
        self,
        address: int,
        size: int,
        assigned: bool = False,
    ) -> None:
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
        return f"<pointer to {self.size} bytes of memory at {str(self)}>"

    def __rich__(self) -> str:
        return f"<pointer to [green]{self.size} bytes[/green] of memory at [cyan]{str(self)}[/cyan]>"  # noqa

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

    def free(self) -> None:
        self.ensure_valid()
        c_free(self.make_ct_pointer())
        self.freed = True


def malloc(size: int) -> AllocatedPointer[Any]:
    """Allocate memory for a given size."""
    mem = c_malloc(size)

    if not mem:
        raise AllocationError("failed to allocate memory")

    return AllocatedPointer(mem, size)


def free(target: BaseAllocatedPointer):
    """Free allocated memory."""
    target.free()


def realloc(target: A, size: int) -> A:
    """Resize a memory block created by malloc."""
    addr = c_realloc(target.address, size)

    if not addr:
        raise AllocationError("failed to resize memory")

    target.size = size
    target.address = addr
    return target
