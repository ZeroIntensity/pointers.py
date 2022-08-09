from typing import Dict, Iterator, Optional, TypeVar

from ._cstd import c_calloc
from ._pointer import BaseAllocatedPointer
from .exceptions import AllocationError, NotEnoughChunks

__all__ = ("AllocatedArrayPointer", "calloc")


T = TypeVar("T")


class AllocatedArrayPointer(BaseAllocatedPointer[T]):
    """Class representing memory created by calloc()"""

    def __init__(
        self,
        address: int,
        chunks: int,
        chunk_size: int,
        current_index: int,
        chunk_cache: Optional[Dict[int, "AllocatedArrayPointer[T]"]] = None,
    ) -> None:
        self._address = address
        self._chunk_size = chunk_size
        self._current_index = current_index
        self._chunks = chunks
        self._chunk_cache = chunk_cache or {0: self}
        self._assigned = True
        self._tracked = False
        self._freed = False

        if chunk_cache:
            self._chunk_cache[self.current_index] = self

    @property
    def address(self) -> Optional[int]:
        return self._address

    @property
    def current_index(self) -> int:
        """Current chunk index."""
        return self._current_index

    @property
    def chunks(self) -> int:
        """Number of allocated chunks."""
        return self._chunks

    @property
    def chunk_size(self) -> int:
        """Size of each chunk."""
        return self._chunk_size

    @property
    def size(self) -> int:
        """Size of the current chunk."""
        return self._chunk_size

    @size.setter
    def size(self, value: int) -> None:
        self._chunk_size = value  # this might break things but idk

    def __add__(self, amount: int) -> "AllocatedArrayPointer[T]":
        index: int = self.current_index + amount

        if index > self.chunks:
            raise NotEnoughChunks(
                f"chunk index is {index}, while allocation is {self.chunks}"
            )

        if index < 0:  # for handling __sub__
            raise IndexError("chunk index is below zero")

        if index not in self._chunk_cache:
            self._chunk_cache[index] = AllocatedArrayPointer(
                self.ensure() + (amount * self.size),
                self.chunks,
                self.chunk_size,
                index,
                self._chunk_cache,
            )

        return self._chunk_cache[index]

    def __sub__(self, amount: int) -> "AllocatedArrayPointer[T]":
        return self.__add__(-amount)

    def __repr__(self) -> str:
        return f"<pointer to allocated chunk at {str(self)}>"

    def __rich__(self) -> str:
        return f"<pointer to [green]allocated chunk[/green] at [cyan]{str(self)}[/cyan]>"  # noqa

    def __iter__(self) -> Iterator["AllocatedArrayPointer[T]"]:
        for i in range(self.current_index, self.chunks):
            yield self + i

    def __del__(self):
        pass


def calloc(num: int, size: int) -> AllocatedArrayPointer:
    """Allocate a number of blocks with a given size."""
    address: int = c_calloc(num, size)

    if not address:
        raise AllocationError("failed to allocate memory")

    return AllocatedArrayPointer(address, num, size, 0)
