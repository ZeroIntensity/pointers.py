from typing import Callable, Optional, TypeVar

from _pointers import run_stack_callback

from .base_pointers import BaseAllocatedPointer, IterDereferencable
from .util import handle

__all__ = ("StackAllocatedPointer", "acquire_stack_alloc", "stack_alloc")


T = TypeVar("T")
A = TypeVar("A", bound=BaseAllocatedPointer)


class StackAllocatedPointer(IterDereferencable[T], BaseAllocatedPointer[T]):
    """Pointer to allocated memory."""

    def __init__(
        self,
        address: int,
        size: int,
        assigned: bool = False,
    ) -> None:
        """
        Args:
            address: Address of the allocated memory.
            size: Size of the allocated memory.
            assigned: Whether an object is currently inside the memory.
        """
        self._address = address
        self._size = size
        self._freed = False
        self._assigned = assigned

    @property
    def address(self) -> Optional[int]:
        return self._address

    @address.setter
    def address(self, value: int) -> None:
        self._address = value

    def __repr__(self) -> str:
        return (
            f"StackAllocatedPointer(address={self.address}, size={self.size})"  # noqa
        )

    def __add__(self, amount: int):
        return StackAllocatedPointer(
            self.ensure() + amount,
            self.size,
            self.assigned,
        )

    def __sub__(self, amount: int):
        return StackAllocatedPointer(
            self.ensure() - amount,
            self.size,
            self.assigned,
        )

    def free(self) -> None:
        raise ValueError(
            "pointers to items on the stack may not be freed dynamically",
        )


@handle
def stack_alloc(size: int):
    """Get a callback with a pointer to stack allocated memory."""

    def decorator(
        func: Callable[[StackAllocatedPointer], T],
    ) -> Callable[[], T]:
        def wrapper():
            return run_stack_callback(size, StackAllocatedPointer, func)

        return wrapper

    return decorator


def acquire_stack_alloc(size: int):
    """Execute a callback with a pointer to stack allocated memory."""

    def decorator(func: Callable[[StackAllocatedPointer], T]) -> T:
        def wrapper():
            return run_stack_callback(size, StackAllocatedPointer, func)

        return wrapper()

    return decorator
