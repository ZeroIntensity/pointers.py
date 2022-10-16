from typing import Dict, Iterator, Optional, TypeVar

from ._cstd import c_calloc, c_free
from .base_pointers import BaseAllocatedPointer
from .exceptions import AllocationError
from .util import handle

__all__ = ("AllocatedArrayPointer", "calloc")

T = TypeVar("T")


# FOR FUTURE REFERENCE:

# _chunk_store is needed to hold each index in the pointer array accordingly.
# We can't just lookup each index via a memory offset,
# since we can't verify that the memory actually contains something.

# If the memory is empty, then Python will segfault as it can't convert it to
# a PyObject*.


# TODO: make this implementation better


class AllocatedArrayPointer(BaseAllocatedPointer[T]):
    """Pointer to an allocated array."""

    def __init__(
        self,
        address: int,
        chunks: int,
        chunk_size: int,
        current_index: int,
        chunk_store: Optional[Dict[int, "AllocatedArrayPointer[T]"]] = None,
        freed: bool = False,
        origin_address: Optional[int] = None,
    ) -> None:
        self._origin_address = origin_address or address
        self._address = address
        self._size = chunk_size
        self._current_index = current_index
        self._chunks = chunks
        self._chunk_store = chunk_store or {0: self}
        self._assigned = True
        self._tracked = False
        self._freed = freed

        if chunk_store:
            self._chunk_store[self.current_index] = self

    @property  # type: ignore
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

    def _get_chunk_at(self, index: int) -> "AllocatedArrayPointer[T]":
        if index > self.chunks:
            raise IndexError(
                f"index is {index}, while allocation is {self.chunks}",
            )

        if index < 0:  # for handling __sub__
            raise IndexError("index is below zero")

        if index not in self._chunk_store:
            self._chunk_store[index] = AllocatedArrayPointer(
                self._origin_address + (index * self.size),
                self.chunks,
                self.size,
                index,
                self._chunk_store,
                self._freed,
                self._origin_address,
            )

        return self._chunk_store[index]

    def __add__(self, amount: int) -> "AllocatedArrayPointer[T]":
        self.ensure_valid()
        return self._get_chunk_at(self._current_index + amount)

    def __sub__(self, amount: int) -> "AllocatedArrayPointer[T]":
        return self.__add__(-amount)

    def __repr__(self) -> str:
        return f"AllocatedArrayPointer(address={self.address}, current_index={self.current_index})"  # noqa

    def __iter__(self) -> Iterator["AllocatedArrayPointer[T]"]:
        for i in range(self.current_index, self.chunks):
            yield self + i

    def __getitem__(self, index: int) -> "AllocatedArrayPointer[T]":
        return self._get_chunk_at(index)

    def __setitem__(self, index: int, value: T) -> None:
        chunk = self._get_chunk_at(index)
        chunk <<= value

    @handle
    def free(self) -> None:
        first = self[0]
        first.ensure_valid()

        for i in range(self._chunks):  # using __iter__ breaks here
            chunk = self._get_chunk_at(i)
            chunk.freed = True

        c_free(first.make_ct_pointer())


def calloc(num: int, size: int) -> AllocatedArrayPointer:
    """Allocate a number of blocks with a given size."""
    address: int = c_calloc(num, size)

    if not address:
        raise AllocationError("failed to allocate memory")

    return AllocatedArrayPointer(address, num, size, 0)
