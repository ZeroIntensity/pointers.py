import ctypes
from typing import Generic, TypeVar, Type, Iterator, Union, Any, Optional
from typing_extensions import ParamSpec
from contextlib import suppress
import faulthandler
from io import UnsupportedOperation
import sys
from _pointers import add_ref, remove_ref, force_set_attr as _force_set_attr
from .exceptions import InvalidSizeError, NullPointerError


__all__ = (
    "Pointer",
    "to_ptr",
    "dereference_address",
    "_",
)

T = TypeVar("T")
A = TypeVar("A")
P = ParamSpec("P")

with suppress(
    UnsupportedOperation
):  # in case its running in idle or something like that
    faulthandler.enable()


def dereference_address(address: int) -> Any:
    """Get the PyObject at the given address."""
    return ctypes.cast(address, ctypes.py_object).value


def force_set_attr(typ: Type[Any], key: str, value: Any) -> None:
    """Force setting an attribute on the target type."""

    if not isinstance(typ, type):
        raise ValueError(
            f"{typ} does not derive from type (did you pass an instance and not a class)?",  # noqa
        )

    _force_set_attr(typ, key, value)


def _make_ptr(data: Union["Pointer[T]", T]) -> "Pointer[T]":
    return data if isinstance(data, Pointer) else to_ptr(data)


class Pointer(Generic[T]):
    """Base class representing a pointer."""

    def __init__(
        self,
        address: int,
        typ: Type[T],
        increment_ref: bool = False,
    ) -> None:
        self._address: Optional[int] = address
        self._type = typ

        if increment_ref:
            add_ref(~self)

    @property
    def address(self) -> Optional[int]:
        """Address of the pointer."""
        return self._address

    @property
    def type(self) -> Type[T]:
        """Type of the pointer."""
        return self._type

    def __repr__(self) -> str:
        return f"<pointer to {self.type.__name__} object at {str(self)}>"  # noqa

    def __rich__(self):
        return f"<pointer to [green]{self.type.__name__}[/green] object at [cyan]{str(self)}[/cyan]>"  # noqa

    def __str__(self) -> str:
        return hex(self.address or 0)

    def dereference(self) -> T:
        """Dereference the pointer."""
        return dereference_address(self.ensure())

    def __iter__(self) -> Iterator[T]:
        """Dereference the pointer."""
        return iter({self.dereference()})

    def __invert__(self) -> T:
        """Dereference the pointer."""
        return self.dereference()

    def assign(self, new: Optional["Pointer[T]"]) -> None:
        """Point to a different address."""
        if not new:
            self._address = None
            return

        if new.type is not self.type:
            raise ValueError("new pointer must be the same type")

        self._address = new.address

    def __rshift__(self, value: Optional[Union["Pointer[T]", T]]):
        """Point to a different address."""
        if not value:
            self.assign(None)
            return self

        self.assign(
            value
            if isinstance(
                value,
                Pointer,
            )
            else to_ptr(value),
        )
        return self

    def move(self, data: "Pointer[T]", unsafe: bool = False) -> None:
        """Move data from another pointer to this pointer. Very dangerous, use with caution."""  # noqa
        if data.type is not self.type:
            raise ValueError("pointer must be the same type")

        deref_a: T = ~data
        deref_b: T = ~self

        size_a: int = sys.getsizeof(deref_a)
        size_b: int = sys.getsizeof(deref_b)

        if (size_b < size_a) and (not unsafe):
            raise InvalidSizeError(
                f"target size may not exceed current size ({size_a} < {size_b})",  # noqa
            )

        bytes_a = (ctypes.c_ubyte * size_a).from_address(data.ensure())
        bytes_b = (ctypes.c_ubyte * size_b).from_address(self.ensure())

        ctypes.memmove(bytes_b, bytes_a, len(bytes_a))

    def __lshift__(self, data: Union["Pointer[T]", T]):
        self.move(_make_ptr(data))
        return self

    def __xor__(self, data: Union["Pointer[T]", T]):
        self.move(_make_ptr(data), unsafe=True)
        return self

    def __del__(self) -> None:
        if self.address:
            remove_ref(~self)

    def __eq__(self, data: object) -> bool:
        if not isinstance(data, Pointer):
            return False

        return data.address == self.address

    def set_attr(self, key: str, value: Any) -> None:
        v: Any = ~self  # mypy gets angry if this isnt any
        if not isinstance(~self, type):
            v = type(v)

        force_set_attr(v, key, value)

    def ensure(self) -> int:
        """Ensure that the pointer is not null."""
        if not self._address:
            raise NullPointerError(
                "cannot perform operation when pointing to None",
            )
        return self._address


def to_ptr(val: T) -> Pointer[T]:
    """Convert a value to a pointer."""
    add_ref(val)
    return Pointer(id(val), type(val))


class _PointerOperatorMagic:
    def __and__(self, obj: T) -> Pointer[T]:
        return to_ptr(obj)

    def __mul__(self, ptr: Pointer[T]) -> T:
        return ~ptr


_ = _PointerOperatorMagic()
