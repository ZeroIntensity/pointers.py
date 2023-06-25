from abc import ABC, abstractmethod
from typing import Generic, Iterator, TypeVar

from typing_extensions import Self, final

from .util import Nullable

__all__ = "BasePointer", "Assignable", "Movable"

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
            raise TypeError(f"{self} is a null pointer")


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


class Movable(BasePointer[T], ABC):
    @final
    def __ilshift__(self, data: T | Self):
        self.move(data)
        return self

    @abstractmethod
    def move(self, target: T | Self) -> None:
        ...
