from .pointer import Pointer, to_ptr
import ctypes
from typing import Optional, Any, Dict, Type, TypeVar, Generic

T = TypeVar("T")
A = TypeVar("A", bound="ctypes.Structure")


class CTypedPointer(Pointer[T], Generic[T]):
    """Class representing a pointer with a known type."""

    def __init__(self, address: int, data_type: Type[T]):
        super().__init__(address, data_type, False)

    @property
    def type(self) -> Type[T]:
        """Type of the pointer."""
        return self._type

    def dereference(self) -> Optional[T]:
        """Dereference the pointer."""
        ctype = self.get_mapped(self.type)
        deref = ctype.from_address(self.address)
        return deref.value  # type: ignore

    @classmethod
    def map_type(cls, data: Any) -> "ctypes._CData":
        typ = cls.get_mapped(type(data))
        return typ(data)

    @staticmethod
    def get_mapped(typ: Any):
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
        try:
            cls.get_mapped(typ)
            return True
        except ValueError:
            return False

    def move(self, data: Pointer[T]) -> None:
        """Move data to the target C object."""
        if data.type is not self.type:
            raise ValueError("pointer must be the same type")

        ptr = ctypes.cast(self.address, ctypes.c_void_p)
        ptr2 = ctypes.pointer(self.map_type(~data))
        ctypes.memmove(ptr, ptr2, ctypes.sizeof(ptr2))


class StructPointer(CTypedPointer[A]):
    """Class representing a pointer to a struct."""

    def __init__(self, address: int, data_type: Type[A]):
        super().__init__(address, data_type)

    def dereference(self) -> A:
        """Dereference the pointer."""
        deref = self.type.from_address(self.address)
        return deref.contents  # type: ignore


class CVoidPointer(CTypedPointer[int]):
    """Class representing a void pointer to a C object."""

    def __init__(self, address: int):
        super().__init__(address, int)

    @property
    def _as_parameter_(self):
        return self.dereference()

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


def cast(ptr: CVoidPointer, data_type: Type[T]) -> CTypedPointer[T]:
    return CTypedPointer(ptr.address, data_type)
