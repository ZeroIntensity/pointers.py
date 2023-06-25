from __future__ import annotations

import ctypes
import sys
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .base_pointer import Assignable, BasePointer, Movable
from .util import Nullable, address_of

T = TypeVar("T")


class PyObjectPointer(Assignable[T, T], Movable[T], BasePointer[T], ABC):
    def __init__(self, address: int) -> None:
        self.address = address
        self.is_null = address == 0

    def assign(self, value: Nullable[T]) -> None:
        self.address = address_of(value)

    @abstractmethod
    def move(self, value: T) -> None:
        ...


class StrPointer(PyObjectPointer[str]):
    def move(self, value: str | StrPointer) -> None:
        ...


def to_ptr(obj: T) -> PyObjectPointer[T]:
    ...
