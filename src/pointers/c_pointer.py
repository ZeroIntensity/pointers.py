from .pointer import Pointer
import ctypes
from typing import (
    Optional,
    Any,
    Dict,
    Type,
    TypeVar,
    Generic,
    TYPE_CHECKING,
    Union,
    Tuple,
    Iterator
)
from .exceptions import InvalidSizeError
from _pointers import add_ref, remove_ref

if TYPE_CHECKING:
    from .struct import Struct

T = TypeVar("T")
A = TypeVar("A", bound="Struct")

__all__ = (
    "TypedCPointer",
    "StructPointer",
    "VoidPointer",
    "cast",
    "to_c_ptr",
    "attempt_decode",
    "to_struct_ptr",
)


def _move(
    ptr: ctypes.pointer,
    stream: bytes,
    *,
    unsafe: bool = False,
    target: str = "memory allocation",
):
    """Move data to a C pointer."""
    try:
        if not unsafe:
            ptr.contents[:] = stream
        else:
            ctypes.memmove(ptr, stream, len(stream))
    except ValueError as e:
        raise InvalidSizeError(
            f"object is of size {len(stream)}, while {target} is {len(ptr.contents)}"  # noqa
        ) from e


def attempt_decode(data: bytes) -> Union[str, bytes]:
    """Attempt to decode a string of bytes."""
    try:
        return data.decode()
    except UnicodeDecodeError:
        return data


class StructPointer(Pointer[A]):
    """Class representing a pointer to a struct."""

    def __init__(self, address: int, data_type: Type[A]):
        super().__init__(address, data_type, True)

    @property
    def _as_parameter_(self):
        return self._address


class _BaseCPointer(Pointer[Any], Generic[T]):
    def __init__(self, address: int, size: int):
        super().__init__(address, int, True)
        self._size = size

    @property
    def size(self):
        """Size of the pointer."""
        return self._size

    # i need to repeat these for type safety
    def __iter__(self) -> Iterator[T]:
        """Dereference the pointer."""
        return iter({self.dereference()})

    def __invert__(self) -> T:
        """Dereference the pointer."""
        return self.dereference()

    def _make_stream_and_ptr(
        self,
        data: "_BaseCPointer",
    ) -> Tuple[ctypes.pointer, bytes]:
        bytes_a = (ctypes.c_ubyte * data.size).from_address(data.address)

        return self.make_ct_pointer(), bytes(bytes_a)

    def move(self, data: Pointer[Any], unsafe: bool = False) -> None:
        """Move data to the allocated memory."""
        if not isinstance(data, _BaseCPointer):
            raise ValueError(
                f'"{type(data).__name__}" object is not a valid C pointer',
            )

        ptr, byte_stream = self._make_stream_and_ptr(data)
        _move(ptr, byte_stream, unsafe=unsafe, target="C data")

    def make_ct_pointer(self):
        return ctypes.cast(
            self.address,
            ctypes.POINTER(ctypes.c_char * self.size),
        )

    @classmethod
    def map_type(cls, data: Any) -> "ctypes._CData":
        """Map the specified data to a C type."""
        typ = cls.get_mapped(type(data))
        return typ(data)

    @staticmethod
    def get_mapped(typ: Any):
        """Get the C mapped value of the given type."""
        types: Dict[type, Type["ctypes._CData"]] = {
            bytes: ctypes.c_char_p,
            str: ctypes.c_wchar_p,
            int: ctypes.c_int,
            float: ctypes.c_float,
            bool: ctypes.c_bool,
        }

        res = types.get(typ)

        if not res:
            raise ValueError(f'"{typ.__name__}" is not mappable to a c type')

        return res

    @classmethod
    def is_mappable(cls, typ: Any) -> bool:
        """Whether the specified type is mappable to C."""
        try:
            cls.get_mapped(typ)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_py(data: Type["ctypes._CData"]) -> Type:
        """Map the specified C type to a Python type."""
        types: Dict[Type["ctypes._CData"], type] = {
            ctypes.c_bool: bool,
            ctypes.c_char: bytes,
            ctypes.c_wchar: str,
            ctypes.c_ubyte: int,
            ctypes.c_short: int,
            ctypes.c_int: int,
            ctypes.c_uint: int,
            ctypes.c_long: int,
            ctypes.c_ulong: int,
            ctypes.c_longlong: int,
            ctypes.c_ulonglong: int,
            ctypes.c_size_t: int,
            ctypes.c_ssize_t: int,
            ctypes.c_float: float,
            ctypes.c_double: float,
            ctypes.c_longdouble: float,
            ctypes.c_char_p: bytes,
            ctypes.c_wchar_p: str,
            ctypes.c_void_p: int,
        }

        return types[data]

    @classmethod
    def make_py(cls, data: "ctypes._CData"):
        """Convert the target C value to a Python object."""
        typ = cls.get_py(type(data))
        res = typ(data)

        if typ is bytes:
            res = attempt_decode(res)

        return res

    def __lshift__(self, data: Any):
        """Move data from another pointer to this pointer."""  # noqa
        self.move(data if isinstance(data, _BaseCPointer) else to_c_ptr(data))
        return self


class VoidPointer(_BaseCPointer[int]):
    """Class representing a void pointer to a C object."""

    @property
    def _as_parameter_(self) -> int:
        return self.address

    def dereference(self) -> Optional[int]:
        """Dereference the pointer."""
        deref = ctypes.c_void_p.from_address(self.address)
        return deref.value

    def __repr__(self) -> str:
        return f"<void pointer to {hex(self.address)}>"  # noqa

    def __rich__(self):
        return (
            f"<[green]void[/green] pointer to [cyan]{hex(self.address)}[/cyan]>"  # noqa
        )

    def __del__(self):
        pass


class TypedCPointer(_BaseCPointer[T], Generic[T]):
    """Class representing a pointer with a known type."""

    def __init__(
        self,
        address: int,
        data_type: Type[T],
        size: int,
        alternate_method: bool = True,
        decref: bool = True
    ):
        self._alt = alternate_method
        super().__init__(address, size)
        self._type = data_type
        self._decref = decref

    @property
    def _as_parameter_(self) -> "ctypes.pointer[ctypes._CData]":
        ctype = self.get_mapped(self.type)
        deref = ctype.from_address(self.address)
        return ctypes.pointer(deref)

    def dereference(self) -> T:
        """Dereference the pointer."""
        ctype = self.get_mapped(self.type)
        ptr = (
            ctype.from_address(self.address)
            if not self._alt else
            ctype(self.address)
        )
        return ptr.value  # type: ignore

    def move(self, data: Pointer, unsafe: bool = False) -> None:
        """Move data to the target C object."""
        if data.type is not self.type:
            raise ValueError("pointer must be the same type")

        super().move(data, unsafe)

    def __repr__(self) -> str:
        return f"<typed c pointer to {hex(self.address)}>"  # noqa

    def __rich__(self):
        return f"<[green]typed c[/green] pointer to [cyan]{hex(self.address)}[/cyan]>"  # noqa

    def __del__(self):
        if (self.type is not str) and (self._decref):
            super().__del__()
            remove_ref(~self)


def cast(ptr: VoidPointer, data_type: Type[T]) -> TypedCPointer[T]:
    """Cast a void pointer to a typed pointer."""
    return TypedCPointer(
        ptr.address,
        data_type,
        ptr.size,
        decref=False
    )


def to_c_ptr(data: T) -> TypedCPointer[T]:
    """Convert a python type to a pointer to a C type."""
    ct = TypedCPointer.map_type(
        data,
    )

    add_ref(ct)
    address = ctypes.addressof(ct)
    typ = type(data)

    return TypedCPointer(
        address,
        typ,
        ctypes.sizeof(ct),
        False
    )


def to_struct_ptr(struct: A) -> StructPointer[A]:
    """Convert a struct to a pointer."""
    return StructPointer(id(struct), type(struct))
