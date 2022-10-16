import ctypes
import sys
from typing import TypeVar, Union

from _pointers import add_ref, remove_ref, set_ref

from .base_pointers import NULL, BaseObjectPointer, BasePointer, Nullable
from .exceptions import InvalidSizeError
from .util import handle

T = TypeVar("T")


class Pointer(BaseObjectPointer[T]):
    """Pointer to a `PyObject`"""

    def __repr__(self) -> str:
        return f"Pointer(address={self.address})"

    @handle
    def move(
        self,
        target: Union[T, "BasePointer[T]"],
        *,
        unsafe: bool = False,
    ):
        data = target if isinstance(target, BasePointer) else to_ptr(target)

        if not isinstance(data, BaseObjectPointer):
            raise ValueError(
                "pointer is not pointing to an object",
            )

        deref_a: T = ~data  # type: ignore
        deref_b: T = ~self

        size_a: int = sys.getsizeof(deref_a)
        size_b: int = sys.getsizeof(deref_b)
        refcnt = sys.getrefcount(deref_b)
        refcnt_a = sys.getrefcount(deref_a)

        if (self._origin_size < size_a) and (not unsafe):
            raise InvalidSizeError(
                f"target size may not exceed current size ({size_a} < {size_b})",  # noqa
            )

        if type(deref_a) is not type(deref_b):
            raise TypeError(
                "cannot move object of a different type",
            )

        current_address: int = self.ensure()
        bytes_a = (ctypes.c_ubyte * size_a).from_address(data.ensure())
        bytes_b = (ctypes.c_ubyte * size_b).from_address(current_address)

        self.assign(~data)
        ctypes.memmove(bytes_b, bytes_a, len(bytes_a))
        set_ref(deref_b, (refcnt - 1) + (refcnt_a - 2))

    @classmethod
    def make_from(cls, obj: Nullable[T]) -> "Pointer[T]":
        is_null = obj is NULL
        return Pointer(
            id(obj) if not is_null else None,
            not is_null,
        )


@handle
def to_ptr(obj: Nullable[T]) -> Pointer[T]:
    """Point to the underlying `PyObject`.

    Args:
        obj: Object to point to.

    Returns:
        Created pointer.

    Example:
        ```py
        ptr = to_ptr(1)  # ptr now points to 1
        something = 2
        something_ptr = to_ptr(something)  # points to 2, not "something"
        ```
    """
    add_ref(obj)
    ptr = Pointer.make_from(obj)
    remove_ref(obj)
    return ptr
