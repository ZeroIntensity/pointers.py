from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from .base_pointers import BasePointer
    from .object_pointer import Pointer

from .object_pointer import to_ptr

__all__ = ("_",)

T = TypeVar("T")


class _PointerOperatorMagic:
    def __and__(self, obj: T) -> "Pointer[T]":
        return to_ptr(obj)

    def __mul__(self, ptr: "BasePointer[T]") -> T:
        return ~ptr


_ = _PointerOperatorMagic()
