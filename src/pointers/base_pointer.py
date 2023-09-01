from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import ClassVar, Generic, Iterator, TypeVar

from typing_extensions import Self, final

from .exceptions import NullPointerError
from .util import Nullable

__all__ = "BasePointer", "Assignable", "Movable", "unsafe"

T = TypeVar("T")
A = TypeVar("A")


class BasePointer(Generic[T], ABC):
    address: int
    is_null: bool

    @abstractmethod
    def dereference(self) -> T:
        ...

    @final
    def __iter__(self) -> Iterator[T]:
        return iter({self.dereference()})

    @final
    def __invert__(self) -> T:
        return self.dereference()

    @final
    def __eq__(self, data: object) -> bool:
        if not isinstance(data, BasePointer):
            return False

        return data.address == self.address

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @final
    def __str__(self) -> str:
        return f"{type(self).__name__}(looking at {hex(self.address)})"

    @final
    def _not_null(self) -> None:
        if self.is_null:
            raise NullPointerError(f"{self} is a null pointer")


class Assignable(Generic[T, A], BasePointer[T], ABC):
    def __irshift__(
        self,
        value: A | Self,
    ):
        self.assign(value)
        return self

    @abstractmethod
    def assign(self, value: Nullable[A] | Self) -> None:
        ...


class _UnsafeTransport:
    _global_unsafe: ClassVar[bool] = False


class Movable(BasePointer[T], ABC, _UnsafeTransport):
    _unsafe: bool

    @final
    def __ilshift__(self, data: T | Self):
        self.move(data)
        return self

    @abstractmethod
    def _move(self, target: T | Self, *, safe: bool = True) -> None:
        ...

    @final
    def move(self, target: T | Self) -> None:
        if self._unsafe or self._global_unsafe:
            self.xmove(target)
        else:
            self._move(target)

    @final
    def xmove(self, target: T | Self) -> None:
        self._move(target, safe=False)

    @contextmanager
    def unsafe(self) -> Iterator[Self]:
        try:
            self._unsafe = True
            yield self
        finally:
            self._unsafe = False


@contextmanager
def unsafe():
    try:
        _UnsafeTransport._global_unsafe = True
        yield None
    finally:
        _UnsafeTransport._global_unsafe = False
