import ctypes
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Type, TypeVar

from _pointers import add_ref, remove_ref

from ._utils import get_mapped, map_type
from .base_pointers import BaseCPointer, IterDereferencable, Typed
from .util import handle

if TYPE_CHECKING:
    from .structure import Struct, StructPointer

T = TypeVar("T")
A = TypeVar("A", bound="Struct")

__all__ = (
    "TypedCPointer",
    "VoidPointer",
    "to_c_ptr",
    "cast",
    "to_voidp",
    "array",
    "to_struct_ptr",
)


class VoidPointer(BaseCPointer[Any]):
    """Class representing a void pointer to a C object."""

    @property
    def size(self) -> int:
        return self._size

    @property  # type: ignore
    @handle
    def _as_parameter_(self) -> ctypes.c_void_p:
        return ctypes.c_void_p(self.address)

    @handle
    def dereference(self) -> Optional[int]:
        deref = ctypes.c_void_p.from_address(self.ensure())
        return deref.value

    def __repr__(self) -> str:
        return f"VoidPointer(address={self.address}, size={self.size})"

    def _cleanup(self) -> None:
        pass


class _CDeref(Typed[T], IterDereferencable[T], ABC):
    @abstractmethod
    def address(self) -> Optional[int]:
        ...

    @property
    @abstractmethod
    def decref(self) -> bool:
        """Whether the target objects reference count should be decremented when the pointer is garbage collected."""  # noqa
        ...

    @handle
    def _cleanup(self) -> None:
        if self.address:
            if (type(~self) is not str) and (self.decref):
                remove_ref(~self)


class _TypedPointer(_CDeref[T], Typed[T], BaseCPointer[T]):
    """Class representing a pointer with a known type."""

    def __init__(
        self,
        address: int,
        data_type: Type[T],
        size: int,
        void_p: bool = True,
        decref: bool = True,
        alt: bool = False,
    ) -> None:
        self._void_p = void_p
        super().__init__(address, size)
        self._type = data_type
        self._decref = decref
        self._alt = alt

    @property
    def alt(self) -> bool:
        """Whether to use the alternative method for dereferencing."""
        return self._alt

    @property
    def size(self) -> int:
        return self._size

    @property
    def decref(self) -> bool:
        return self._decref

    @property
    def type(self):
        return self._type


class TypedCPointer(_TypedPointer[T]):
    """Class representing a pointer with a known type."""

    @property
    def address(self) -> Optional[int]:
        return self._address

    @property  # type: ignore
    @handle
    def _as_parameter_(self):
        ctype = get_mapped(self.type)
        deref = ctype.from_address(self.ensure())
        value = deref.value  # type: ignore

        if isinstance(value, (TypedCPointer, VoidPointer)):
            return ctypes.pointer(value._as_parameter_)  # type: ignore

        return ctypes.pointer(deref)

    @handle
    def dereference(self) -> T:
        """Dereference the pointer."""
        ctype = get_mapped(self.type)

        if (ctype is ctypes.c_char_p) and (self._alt):
            res = ctypes.c_char_p(self.ensure()).value
            return res  # type: ignore

        ptr = (
            ctype.from_address(self.ensure())
            if not self._void_p
            else ctypes.cast(
                ctypes.c_void_p(self.address), ctypes.POINTER(ctype)
            )  # fmt: off
        )
        return ptr.value if not self._void_p else ptr.contents.value  # type: ignore # noqa

    def __iter__(self) -> Iterator[T]:
        """Dereference the pointer."""
        return iter({self.dereference()})

    def __repr__(self) -> str:
        return f"TypedCPointer(address={self.address}, size={self.size})"


class CArrayPointer(_CDeref[List[T]], Typed[Type[T]], BaseCPointer[List[T]]):
    """Class representing a pointer to a C array."""

    def __init__(
        self,
        address: int,
        size: int,
        length: int,
        typ: Type[T],
    ):
        self._length = length
        self._type = typ
        self._decref = False
        super().__init__(address, size)

    @property
    def decref(self) -> bool:
        return self._decref

    @property
    def type(self) -> Type[T]:  # type: ignore
        return self._type

    @property  # type: ignore
    @handle
    def _as_parameter_(self) -> "ctypes.Array[ctypes._CData]":
        ctype = get_mapped(self.type)

        deref = (ctype * self._length).from_address(self.ensure())
        return deref

    @handle
    def dereference(self) -> List[T]:
        """Dereference the pointer."""
        array = self._as_parameter_
        return [array[i] for i in range(self._length)]  # type: ignore

    def __repr__(self) -> str:
        return f"CArrayPointer(address={self.address}, size={self.size})"

    def __getitem__(self, index: int) -> T:
        array = ~self
        return array[index]


@handle
def cast(ptr: VoidPointer, data_type: Type[T]) -> TypedCPointer[T]:
    """Cast a void pointer to a typed pointer."""

    return TypedCPointer(
        ptr.ensure(),
        data_type,
        ptr.size,
        decref=False,
        void_p=True,
        alt=True,
    )


def to_voidp(ptr: TypedCPointer[Any]) -> VoidPointer:
    """Cast a typed pointer to a void pointer."""

    return VoidPointer(ptr.ensure(), ptr.size)


def to_c_ptr(data: T) -> TypedCPointer[T]:
    """Convert a python type to a pointer to a C type."""
    ct = map_type(data)

    add_ref(ct)
    address = ctypes.addressof(ct)
    typ = type(data)

    return TypedCPointer(address, typ, ctypes.sizeof(ct), False)


def to_struct_ptr(struct: A) -> "StructPointer[A]":
    """Convert a struct to a pointer."""
    from .structure import StructPointer

    return StructPointer(id(struct))


@handle
def array(*seq: T) -> CArrayPointer[T]:
    f_type = type(seq[0])

    for i in seq:
        if type(i) is not f_type:  # dont use isinstance here
            raise ValueError(
                "all values in the array must be the same type",
            )

    length = len(seq)
    ctype = get_mapped(f_type)
    arr = (ctype * length)(*seq)  # type: ignore
    add_ref(arr)

    return CArrayPointer(
        ctypes.addressof(arr),
        ctypes.sizeof(arr),
        length,
        f_type,  # type: ignore
    )
