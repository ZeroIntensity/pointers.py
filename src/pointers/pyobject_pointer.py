from typing import Generic, TypeVar

from .base_pointer import Assignable, BasePointer, Movable

T = TypeVar("T")

class PyObjectPointer(Assignable[T, T], Movable[T], BasePointer[T]):
    def __init__(self, address: int) -> None:
        self.address = address
        self.is_null = False

    def assign() -> None:
        ...
