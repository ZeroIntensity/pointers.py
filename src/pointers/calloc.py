from .exceptions import (
    AllocationError,
    NotEnoughChunks,
    CallocInheritanceError
)
from .malloc import MallocPointer
from ._cstd import c_calloc
from typing import Iterator, Optional, Dict, TypeVar, Generic
import ctypes

__all__ = ("CallocPointer", "calloc")


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

        bytes_a = (ctypes.c_ubyte * 24) \
            .from_address(id(0))

        ctypes.memmove(address, bytes_a, len(bytes_a))

    def dereference(self) -> T:
        """Dereference the pointer."""

        return super().dereference()

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

    def __add__(self, amount: int) -> "CallocPointer":
        index: int = self.current_index + amount

        if index > self.chunks:
            raise NotEnoughChunks(
                f"chunk index is {index}, while allocation is {self.chunks}"
            )

        if index < 0:  # for handling __sub__
            raise IndexError("chunk index is below zero")

        if index not in self._chunk_cache:
            self._chunk_cache[index] = CallocPointer(
                self.address + (amount * self.size),
                self.chunks,
                self.chunk_size,
                index,
                self._chunk_cache,  # type: ignore
            )

        return self._chunk_cache[index]

    def __sub__(self, amount: int) -> "CallocPointer":
        return self.__add__(-amount)

    def __repr__(self) -> str:
        return f"<pointer to allocated chunk at {hex(self.address)}>"

    def __rich__(self) -> str:
        return f"<pointer to [green]allocated chunk[/green] at [cyan]{hex(self.address)}[/cyan]>"  # noqa

    def __iter__(self) -> Iterator["CallocPointer"]:
        for i in range(self.current_index, self.chunks):
            yield self + i

    def __getitem__(self, i) -> None:
        raise CallocInheritanceError("""Subscription not allowed for Calloc chunks.""")  # noqa

    def __setitem__(self, i) -> None:
        raise CallocInheritanceError("""Item assignment not allowed for Calloc chunks.""")  # noqa

    def __ilshift__(self, func) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__ilshift__'" # noqa
            )

    def __irshift__(self, func) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__irshift__'" # noqa
            )

    def __abs__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__abs__'" # noqa
            )

    def __add__(self, other)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__add__'" # noqa
            )

    def __and__(self, other)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__and__'" # noqa
            )

    def __bool__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__bool__'" # noqa
            )

    def __complex__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__complex__'" # noqa
            )


    def __dlpack__(self) -> None: # inherited by np
        raise CallocInheritanceError(
                f"Calloc does not inherit '__dlpack__'" # noqa
            )

    def __eq__(self, other)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__eq__'" # noqa
            )

    def __float__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__float__'" # noqa
            )

    def __format__(self, string: str)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__format__'" # noqa
            )

    def __ge__(self, other)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__ge__'" # noqa
            )

    def __gt__(self, other)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__gt__'" # noqa
            )

    def __hash__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__hash__'" # noqa
            )

    def __hex__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__hex__'" # noqa
            )

    def __int__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__int__'" # noqa
            )

    def __index__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__index__'" # noqa
            )

    def __le__(self, other)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__le__'" # noqa
            )

    def __lt__(self, other)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__lt__'" # noqa
            )

    def __matmul__(self, other )-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__matmul__'" # noqa
            )

    def __mod__(self, other )-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__mod__'" # noqa
            )

    def __mul__(self, other )-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__mul__'" # noqa
            )

    def __ne__(self, other )-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__ne__'" # noqa
            )

    def __neg__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__neg__'" # noqa
            )

    def __nonzero__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__nonzero__'" # noqa
            )

    def __oct__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__oct__'" # noqa
            )

    def __or__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__or__'" # noqa
            )

    def __pos__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__pos__'" # noqa
            )

    def __pow__(self, other )-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__pow__'" # noqa
            )

    def __truediv__(self, other)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__truediv__'" # noqa
            )

    def __trunc__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__trunc__'" # noqa
            )

    def __unicode__(self)-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__unicode__'" # noqa
            )

    def __rxor__(self, other )-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__rxor__'" # noqa
            )

    def __xor__(self, other )-> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__xor__'" # noqa
            )

    def __iadd__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__iadd__'" # noqa
            )

    def __iand__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__iand__'" # noqa
            )

    def __idiv__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__idiv__'" # noqa
            )

    def __ifloordiv__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__ifloordiv__'" # noqa
            )

    def __imod__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__imod__'" # noqa
            )

    def __imul__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__imul__'" # noqa
            )

    def __ior__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__ior__'" # noqa
            )

    def __ipow__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__ipow__'" # noqa
            )

    def __isub__(self, other) -> None:
        raise CallocInheritanceError(
                f"Calloc does not inherit '__isub__'" # noqa
            )


def calloc(num: int, size: int) -> CallocPointer:
    """Allocate a number of blocks with a given size."""
    address: int = c_calloc(num, size)

    if not address:
        raise AllocationError("failed to allocate memory")

    return CallocPointer(address, num, size, 0)
