from typing import TYPE_CHECKING, Any, Type, TypeVar

from _pointers import force_set_attr as _force_set_attr

if TYPE_CHECKING:
    from ._pointer import BasePointer

from .object_pointer import Pointer, to_ptr

__all__ = (
    "_",
    "force_set_attr",
)

T = TypeVar("T")


def force_set_attr(typ: Type[Any], key: str, value: Any) -> None:
    """Force setting an attribute on the target type."""

    if not isinstance(typ, type):
        raise ValueError(
            f"{typ} does not derive from type (did you pass an instance and not a class)?",  # noqa
        )

    _force_set_attr(typ, key, value)


class _PointerOperatorMagic:
    def __and__(self, obj: T) -> "Pointer[T]":
        return to_ptr(obj)

    def __mul__(self, ptr: "BasePointer[T]") -> T:
        return ~ptr


_ = _PointerOperatorMagic()
