from .exceptions import AllocationError, NotEnoughChunks
from .malloc import MallocPointer
from ._cstd import c_calloc
from typing import Iterator, Optional, Dict, TypeVar, Generic, Union, Type
from .pointer import Pointer
import ctypes

__all__ = ("CallocPointer", "calloc", "calloc_safe")


class RepresentsNone:  # have to use this to allow storing null values
    """Class for representing a none value cache."""

    pass


T = TypeVar("T")


class CallocPointer(MallocPointer, Generic[T]):
    """Class representing memory created by calloc()"""

    def __init__(
        self,
        address: int,
        chunks: int,
        chunk_size: int,
        current_index: int,
        chunk_cache: Optional[Dict[int, "CallocPointer"]] = None,
        safe: bool = False,
    ) -> None:
        self._address = address
        self._chunk_size = chunk_size
        self._current_index = current_index
        self._chunks = chunks
        self._freed = False
        self._chunk_cache = chunk_cache or {0: self}
        self._assigned = True

        if chunk_cache:
            self._chunk_cache[self.current_index] = self

        self._safe = safe
        self._value_cache: Union[T, Type[RepresentsNone]] = RepresentsNone

        bytes_a = (ctypes.c_ubyte * 24) \
            .from_address(id(0))

        ctypes.memmove(address, bytes_a, len(bytes_a))

    def dereference(self) -> T:
        """Dereference the pointer."""

        if self._safe:
            if self._value_cache is RepresentsNone:
                raise MemoryError(
                    "cannot dereference pointer that has no value"
                )

            return self._value_cache  # type: ignore
            # ^^ false positive

        return super().dereference()

    def move(self, data: Pointer[T]) -> None:
        """Move data to the allocated memory."""
        self._value_cache = ~data
        super().move(data)

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

    @property
    def safe(self) -> bool:
        """Whether value caching is enabled."""
        return self._safe

    def __add__(self, amount: int) -> "CallocPointer":
        index: int = self.current_index + amount

        if index > self.chunks:
            raise NotEnoughChunks(
                f"chunk index is {index}, while allocation is {self.chunks}"
            )

        if index not in self._chunk_cache:
            self._chunk_cache[index] = CallocPointer(
                self.address + amount,
                self.chunks,
                self.chunk_size,
                index,
                self._chunk_cache,  # type: ignore
                safe=self.safe,
            )

        return self._chunk_cache[index]

    def __sub__(self, amount: int) -> "CallocPointer":
        index: int = self.current_index - amount

        if index < 0:
            raise IndexError("chunk index is below zero")

        return self._chunk_cache[index]

    def __repr__(self) -> str:
        return f"<pointer to allocated chunk at {hex(self.address)}>"

    def __iter__(self) -> Iterator["CallocPointer"]:
        for i in range(self.current_index, self.chunks):
            yield self + i


def calloc(num: int, size: int, safe: bool = False) -> CallocPointer:
    """Allocate a number of blocks with a given size."""
    address: int = c_calloc(num, size)

    if not address:
        raise AllocationError("failed to allocate memory")

    return CallocPointer(address, num, size, 0, safe=safe)


def calloc_safe(num: int, size: int) -> CallocPointer:
    """Allocate a number of blocks with a given size."""
    return calloc(num, size, True)
