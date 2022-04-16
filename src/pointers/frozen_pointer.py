from .pointer import Pointer
from typing import TypeVar, NoReturn
from .exceptions import IsFrozenError

__all__ = (
    'FrozenPointer',
    'to_const_ptr'
)


T = TypeVar("T")


class FrozenPointer(Pointer[T]):
    def assign(self, _: Pointer[T]) -> NoReturn:
        """Point to a different address."""
        raise IsFrozenError("this pointer is frozen")


def to_const_ptr(val: T) -> FrozenPointer[T]:
    """Convert a value to a pointer."""
    return FrozenPointer(id(val), type(val))
