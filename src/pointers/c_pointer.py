from .pointer import Pointer, to_ptr, dereference_address
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
)

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
)


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
        self.__ref = dereference_address(
            address
        )  # this needs to be here to stop garbage collection

    def __getattr__(self, name: str):
        if name == "__ref":
            raise Exception
        return super().__getattribute__(name)


class VoidPointer(Pointer[int]):
    """Class representing a void pointer to a C object."""

    def __init__(self, address: int):
        super().__init__(address, int, False)

    @property
    def _as_parameter_(self) -> int:
        return self.address

    def dereference(self) -> Optional[int]:
        """Dereference the pointer."""
        deref = ctypes.c_void_p.from_address(self.address)
        return deref.value

    def __lshift__(self, data: Any):
        """Move data from another pointer to this pointer. Very dangerous, use with caution."""  # noqa
        self.move(data if isinstance(data, Pointer) else to_ptr(data))
        return self

    def __repr__(self) -> str:
        return f"<void pointer to {hex(self.address)}>"  # noqa

    def __rich__(self):
        return (
            f"<[green]void[/green] pointer to [cyan]{hex(self.address)}[/cyan]>"  # noqa
        )

    def move(self, data: Pointer) -> None:
        """Move data to the target C object."""
        ptr = ctypes.cast(self.address, ctypes.c_void_p)
        ptr2 = ctypes.pointer(self.map_type(~data))
        ctypes.memmove(ptr, ptr2, ctypes.sizeof(ptr2))

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


class TypedCPointer(VoidPointer, Generic[T]):
    """Class representing a pointer with a known type."""

    def __init__(self, address: int, data_type: Type[T]):
        super().__init__(address)
        self._type = data_type

    @property
    def _as_parameter_(self):
        ctype = self.get_mapped(self.type)
        deref = ctype.from_address(self.address)
        return ctypes.pointer(deref)

    @property
    def type(self) -> Type[T]:
        """Type of the pointer."""
        return self._type

    def dereference(self) -> Optional[T]:
        """Dereference the pointer."""
        ctype = self.get_mapped(self.type)
        deref = ctype.from_address(self.address)
        return deref.value  # type: ignore

    def move(self, data: Pointer[T]) -> None:
        """Move data to the target C object."""
        if data.type is not self.type:
            raise ValueError("pointer must be the same type")

        super().move(data)

    def __repr__(self) -> str:
        return f"<typed c pointer to {hex(self.address)}>"  # noqa

    def __rich__(self):
        return f"<[green]typed c[/green] pointer to [cyan]{hex(self.address)}[/cyan]>"  # noqa


def cast(ptr: VoidPointer, data_type: Type[T]) -> TypedCPointer[T]:
    """Cast a void pointer to a typed pointer."""
    return TypedCPointer(ptr.address, data_type)


def to_c_ptr(data: T) -> TypedCPointer[T]:
    """Convert a python type to a pointer to a C type."""
    ct = TypedCPointer.map_type(
        data if not isinstance(data, str) else data.encode(),
    )
    address = ctypes.addressof(ct)

    ptr = ctypes.cast(address, ctypes.c_void_p)
    ptr2 = ctypes.pointer(TypedCPointer.map_type(data))
    ctypes.memmove(ptr, ptr2, ctypes.sizeof(ptr2))

    return TypedCPointer(address, type(data))
