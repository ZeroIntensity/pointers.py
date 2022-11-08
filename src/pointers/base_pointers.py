import ctypes
import sys
import warnings
import weakref
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import (
    Any, Generic, Iterator, Optional, Tuple, Type, TypeVar, Union
)

from typing_extensions import final

from _pointers import add_ref, remove_ref

from ._utils import deref, force_set_attr, move_to_mem
from .exceptions import DereferenceError, FreedMemoryError, NullPointerError
from .util import NULL, Nullable, handle

__all__ = (
    "BasePointer",
    "BaseObjectPointer",
    "BasicPointer",
    "BaseCPointer",
    "BaseAllocatedPointer",
    "Dereferencable",
    "IterDereferencable",
)

warnings.simplefilter("always", DeprecationWarning)

T = TypeVar("T")
A = TypeVar("A", bound="BasicPointer")


class BasicPointer(ABC):
    """Base class representing a pointer with no operations."""

    @property
    @abstractmethod
    def address(self) -> Optional[int]:
        """Address that the pointer is looking at."""
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @final
    def __str__(self) -> str:
        return f"{type(self).__name__}({hex(self.address or 0)})"

    @abstractmethod
    def _cleanup(self) -> None:
        ...

    @final
    def __eq__(self, data: object) -> bool:
        if not isinstance(data, BasePointer):
            return False

        return data.address == self.address

    @final
    def ensure(self) -> int:
        """Ensure that the pointer is not null.

        Raises:
            NullPointerError: Address of pointer is `None`

        Returns:
            Address of the pointer.

        Example:
            ```py
            ptr = to_ptr(NULL)
            address = ptr.ensure()  # NullPointerError
            ptr >>= 1
            address = ptr.ensure()  # works just fine
            ```"""

        if not self.address:
            raise NullPointerError("pointer is NULL")
        return self.address


class Movable(ABC, Generic[T, A]):
    @abstractmethod
    def move(
        self,
        data: Union[A, T],
        *,
        unsafe: bool = False,
    ) -> None:
        ...

    def __ilshift__(self, data: Union[A, T]):
        self.move(data)
        return self

    def __ixor__(self, data: Union[A, T]):
        self.move(data, unsafe=True)
        return self


class Dereferencable(ABC, Generic[T]):
    """Abstract class for an object that may be dereferenced."""

    @abstractmethod
    def dereference(self) -> T:
        """Dereference the pointer.

        Returns:
            Value at the pointers address."""
        ...

    @final
    def __invert__(self) -> T:
        """Dereference the pointer."""
        return self.dereference()


class IterDereferencable(Dereferencable[T], Generic[T]):
    """
    Abstract class for an object that may be dereferenced via * (`__iter__`)
    """

    def __iter__(self) -> Iterator[T]:
        """Dereference the pointer."""
        return iter({self.dereference()})


class BasePointer(
    Dereferencable[T],
    Movable[T, "BasePointer[T]"],
    BasicPointer,
    ABC,
    Generic[T],
):
    """Base class representing a pointer."""

    @property
    @abstractmethod
    def address(self) -> Optional[int]:
        """Address that the pointer is looking at."""
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    def _cleanup(self) -> None:
        ...


class Typed(ABC, Generic[T]):
    """Base class for a pointer that has a type attribute."""

    @property
    @abstractmethod
    def type(self) -> T:
        """Type of the value at the address."""
        ...


class Sized(ABC):
    """Base class for a pointer that has a size attribute."""

    @abstractmethod
    def ensure(self) -> int:
        ...

    @property
    @abstractmethod
    def size(self) -> int:
        """Size of the target value."""
        ...

    @handle
    @final
    def make_ct_pointer(self) -> "ctypes._PointerLike":
        """Convert the address to a ctypes pointer.

        Returns:
            The created ctypes pointer.
        """
        return ctypes.cast(
            self.ensure(),
            ctypes.POINTER(ctypes.c_char * self.size),
        )

    @abstractmethod
    def _make_stream_and_ptr(
        self,
        size: int,
        address: int,
    ) -> Tuple["ctypes._PointerLike", bytes]:
        ...


class BaseObjectPointer(
    Typed[Type[T]],
    IterDereferencable[T],
    BasePointer[T],
    ABC,
):
    """Abstract class for a pointer to a Python object."""

    def __init__(
        self,
        address: Optional[int],
        increment_ref: bool = False,
    ) -> None:
        """
        Args:
            address: Address of the underlying value.
            typ: Type of the pointer.
            increment_ref: Should the reference count on the target object get incremented.
        """  # noqa
        self._address: Optional[int] = address

        if increment_ref and address:
            add_ref(~self)

        self._origin_size = sys.getsizeof(~self if address else None)
        weakref.finalize(self, self._cleanup)

    @property
    def type(self) -> Type[T]:
        warnings.warn(
            "BaseObjectPointer.type is deprecated, please use type(~ptr) instead",  # noqa
            DeprecationWarning,
        )

        return type(~self)

    @handle
    def set_attr(self, key: str, value: Any) -> None:
        v: Any = ~self  # mypy gets angry if this isnt any
        if not isinstance(~self, type):
            v = type(v)

        force_set_attr(v, key, value)

    @handle
    def assign(
        self,
        target: Nullable[Union["BaseObjectPointer[T]", T]],
    ) -> None:
        """Point to a new address.

        Args:
            target: New pointer or value to look at.
        """
        if target is NULL:
            self._address = None
            return

        new: BasePointer[T] = self._get_ptr(target)  # type: ignore

        if not isinstance(new, BaseObjectPointer):
            raise ValueError(
                "can only point to object pointer",
            )

        with suppress(NullPointerError):
            remove_ref(~self)

        self._address = new.address
        add_ref(~self)

    @property
    def address(self) -> Optional[int]:
        return self._address

    @handle
    def dereference(self) -> T:
        return deref(self.ensure())

    def __irshift__(
        self,
        value: Nullable[Union["BaseObjectPointer[T]", T]],
    ):
        self.assign(value)
        return self

    @classmethod
    @abstractmethod
    def make_from(cls, obj: T) -> "BaseObjectPointer[T]":
        """Create a new instance of the pointer.

        Args:
            obj: Object to create pointer to.

        Returns:
            Created pointer.

        Example:
            ```py
            ptr = Pointer.make_from(1)
            ```"""
        ...

    @classmethod
    def _get_ptr(cls, obj: Union[T, "BasePointer[T]"]) -> "BasePointer[T]":
        return (
            obj
            if isinstance(
                obj,
                BasePointer,
            )
            else cls.make_from(obj)
        )

    def _cleanup(self) -> None:
        if self.address:
            remove_ref(~self)


class BaseCPointer(
    IterDereferencable[T],
    Movable[T, "BaseCPointer[T]"],
    BasicPointer,
    Sized,
    ABC,
):
    def __init__(self, address: int, size: int):
        self._address = address
        self._size = size
        weakref.finalize(self, self._cleanup)

    @property
    def address(self) -> Optional[int]:
        return self._address

    def _make_stream_and_ptr(
        self,
        size: int,
        address: int,
    ) -> Tuple["ctypes._PointerLike", bytes]:
        bytes_a = (ctypes.c_ubyte * size).from_address(address)
        return self.make_ct_pointer(), bytes(bytes_a)

    @handle
    def move(
        self,
        data: Union["BaseCPointer[T]", T],
        *,
        unsafe: bool = False,
    ) -> None:
        """Move data to the target address."""
        if not isinstance(data, BaseCPointer):
            raise ValueError(
                f'"{type(data).__name__}" object is not a valid C pointer',
            )

        ptr, byte_stream = self._make_stream_and_ptr(
            data.size,
            data.ensure(),
        )
        move_to_mem(ptr, byte_stream, unsafe=unsafe, target="C data")

    def __ilshift__(self, data: Union["BaseCPointer[T]", T]):
        self.move(data)
        return self

    def __ixor__(self, data: Union["BaseCPointer[T]", T]):
        self.move(data, unsafe=True)
        return self

    @handle
    def make_ct_pointer(self):
        return ctypes.cast(
            self.ensure(),
            ctypes.POINTER(ctypes.c_char * self.size),
        )

    @abstractmethod
    def _as_parameter_(self) -> "ctypes._CData":
        """Convert the pointer to a ctypes pointer."""
        ...

    @abstractmethod
    def _cleanup(self) -> None:
        ...


class BaseAllocatedPointer(BasePointer[T], Sized, ABC):
    @property
    @abstractmethod
    def address(self) -> Optional[int]:
        ...

    @address.setter
    def address(self, value: int) -> None:
        ...

    @property
    def freed(self) -> bool:
        """Whether the allocated memory has been freed."""
        return self._freed

    @freed.setter
    def freed(self, value: bool) -> None:
        self._freed = value

    @property
    def assigned(self) -> bool:
        """Whether the allocated memory has been assigned a value."""
        return self._assigned

    @assigned.setter
    def assigned(self, value: bool) -> None:
        self._assigned = value

    @handle
    def move(
        self,
        data: Union[BasePointer[T], T],
        unsafe: bool = False,
    ) -> None:
        add_ref(data)
        self.ensure_valid()
        from .object_pointer import to_ptr

        data_ptr = data if isinstance(data, BasePointer) else to_ptr(data)

        ptr, byte_stream = self._make_stream_and_ptr(
            sys.getsizeof(~data_ptr),
            data_ptr.ensure(),
        )

        move_to_mem(ptr, byte_stream, unsafe=unsafe)
        self.assigned = True
        remove_ref(data)

    @handle
    def dereference(self) -> T:
        if self.freed:
            raise FreedMemoryError(
                "cannot dereference memory that has been freed",
            )

        if not self.assigned:
            raise DereferenceError(
                "cannot dereference allocated memory that has no value",
            )

        return deref(self.ensure())

    @abstractmethod
    def __add__(self, amount: int) -> "BaseAllocatedPointer[Any]":
        ...

    @abstractmethod
    def __sub__(self, amount: int) -> "BaseAllocatedPointer[Any]":
        ...

    def _cleanup(self) -> None:
        pass

    def _make_stream_and_ptr(
        self,
        size: int,
        address: int,
    ) -> Tuple["ctypes._PointerLike", bytes]:
        if self.freed:
            raise FreedMemoryError("memory has been freed")

        bytes_a = (ctypes.c_ubyte * size).from_address(address)  # fmt: off
        return self.make_ct_pointer(), bytes(bytes_a)

    @abstractmethod
    def free(self) -> None:
        """Free the memory."""
        ...

    def ensure_valid(self) -> None:
        """Ensure the memory has not been freed."""
        if self.freed:
            raise FreedMemoryError(
                f"{self} has been freed",
            )

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = value
