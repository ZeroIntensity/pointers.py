import ctypes
import sys
from typing import Generic, NoReturn, Tuple, TypeVar

from ._cstd import c_free, c_malloc, c_realloc
from .c_pointer import _move
from .exceptions import (
    AllocationError, DereferenceError, FreedMemoryError, IsMallocPointerError
)
from .pointer import Pointer

__all__ = ("MallocPointer", "malloc", "free", "realloc")


T = TypeVar("T")


class MallocPointer(Pointer, Generic[T]):
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
    def freed(self) -> bool:
        """Whether the allocated memory has been freed."""
        return self._freed

    @freed.setter
    def freed(self, value: bool) -> None:
        self._freed = value

    @property
    def assigned(self) -> bool:
        """Whether the allocated memory has been assigned a value."""
        return self._assigned

    @assigned.setter
    def assigned(self, value: bool) -> None:
        self._assigned = value

    @property
    def type(self) -> NoReturn:
        """Type of the pointer."""
        raise IsMallocPointerError(
            "malloc pointers do not have types",
        )

    @property
    def size(self) -> int:
        """Size of the memory."""
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = value

    def assign(self, _) -> NoReturn:
        """Point to a different address."""
        raise IsMallocPointerError("cannot assign to malloc pointer")

    def __repr__(self) -> str:
        return f"<pointer to {self.size} bytes of memory at {str(self)}>"

    def __rich__(self) -> str:
        return f"<pointer to [green]{self.size} bytes[/green] of memory at [cyan]{str(self)}[/cyan]>"  # noqa

    def _make_stream_and_ptr(
        self,
        data: Pointer[T],
    ) -> Tuple[ctypes.pointer, bytes]:
        if self.freed:
            raise FreedMemoryError("memory has been freed")

        bytes_a = (ctypes.c_ubyte * sys.getsizeof(~data)).from_address(
            data.ensure()
        )  # fmt: off

        return self.make_ct_pointer(), bytes(bytes_a)

    def move(self, data: Pointer[T], unsafe: bool = False) -> None:
        """Move data to the allocated memory."""
        ptr, byte_stream = self._make_stream_and_ptr(data)

        _move(ptr, byte_stream, unsafe=unsafe)
        self.assigned = True

    def make_ct_pointer(self):
        return ctypes.cast(
            self.ensure(),
            ctypes.POINTER(ctypes.c_char * self.size),
        )

    def dereference(self):
        """Dereference the pointer."""
        if self.freed:
            raise FreedMemoryError(
                "cannot dereference memory that has been freed",
            )

        if not self.assigned:
            raise DereferenceError(
                "cannot dereference pointer that has no value",
            )

        return super().dereference()

    def __add__(self, amount: int):
        return MallocPointer(self.ensure() + amount, self.size, self.assigned)

    def __sub__(self, amount: int):
        return MallocPointer(self.ensure() - amount, self.size, self.assigned)

    def __del__(self):
        pass


def malloc(size: int) -> MallocPointer:
    """Allocate memory for a given size."""
    mem = c_malloc(size)

    if not mem:
        raise AllocationError("failed to allocate memory")

    return MallocPointer(mem, size)


def free(target: MallocPointer):
    """Free allocated memory."""
    ct_ptr = target.make_ct_pointer()
    c_free(ct_ptr)
    target.freed = True


def realloc(target: MallocPointer, size: int) -> None:
    """Resize a memory block created by malloc."""
    mem = c_realloc(target.address, size)

    if not mem:
        raise AllocationError("failed to resize memory")

    target.size = size
