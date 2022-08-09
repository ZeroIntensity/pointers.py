import ctypes
from typing import (
    TYPE_CHECKING, Any, Dict, Generic, Iterator, List, Optional, Tuple, Type,
    TypeVar, Union
)

from _pointers import add_ref, remove_ref

from .exceptions import InvalidSizeError
from .pointer import Pointer

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
    "array",
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

    def __init__(
        self,
        address: int,
        data_type: Type[A],
        existing: Optional["Struct"] = None,
    ):
        super().__init__(address, data_type, True)
        self._existing = existing

    @property
    def _as_parameter_(self) -> Union[int, ctypes.pointer]:
        existing = self._existing

        if existing:
            return ctypes.pointer(existing.struct)

        return self.ensure()

    def __repr__(self) -> str:
        return f"<pointer to struct at {str(self)}>"


class _BaseCPointer(Pointer[Any], Generic[T]):
    def __init__(self, address: int, size: int):
        super().__init__(address, int, True)
        self._size = size

    @property
    def size(self):
        """Size of the pointer."""
        return self._size

    # i need to repeat these for type safety
    @property
    def type(self) -> T:  # type: ignore
        """Type of the pointer."""
        return self._type  # type: ignore

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
        bytes_a = (ctypes.c_ubyte * data.size).from_address(data.ensure())

        return self.make_ct_pointer(), bytes(bytes_a)

    def move(self, data: Pointer[T], unsafe: bool = False) -> None:
        """Move C data to the target memory."""
        if not isinstance(data, _BaseCPointer):
            raise ValueError(
                f'"{type(data).__name__}" object is not a valid C pointer',
            )

        ptr, byte_stream = self._make_stream_and_ptr(data)
        _move(ptr, byte_stream, unsafe=unsafe, target="C data")

    def make_ct_pointer(self):
        return ctypes.cast(
            self.ensure(),
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
    def get_py(
        data: Type["ctypes._CData"],
    ) -> Type[Any]:
        """Map the specified C type to a Python type."""
        if data.__name__.startswith("LP_"):
            return Pointer

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

    def __lshift__(self, data: T):  # type: ignore
        """Move data from another pointer to this pointer."""  # noqa
        self.move(data if isinstance(data, _BaseCPointer) else to_c_ptr(data))
        return self


class VoidPointer(_BaseCPointer[int]):
    """Class representing a void pointer to a C object."""

    @property
    def _as_parameter_(self) -> ctypes.c_void_p:
        return ctypes.c_void_p(self.address)

    def dereference(self) -> Optional[int]:
        """Dereference the pointer."""
        deref = ctypes.c_void_p.from_address(self.ensure())
        return deref.value

    def __repr__(self) -> str:
        return f"<void pointer to {str(self)}>"  # noqa

    def __rich__(self):
        return f"<[green]void[/green] pointer to [cyan]{str(self)}[/cyan]>"  # noqa

    def __del__(self):
        pass


class _TypedPointer(_BaseCPointer[Any], Generic[T]):
    """Class representing a pointer with a known type."""

    def __init__(
        self,
        address: int,
        data_type: Type[T],
        size: int,
        void_p: bool = True,
        decref: bool = True,
    ):
        self._void_p = void_p
        super().__init__(address, size)
        self._type = data_type
        self._decref = decref

    def move(self, data: Pointer, unsafe: bool = False) -> None:
        """Move data to the target C object."""
        if data.type is not self.type:
            raise ValueError("pointer must be the same type")

        super().move(data, unsafe)

    def __repr__(self) -> str:
        return f"<typed c pointer to {str(self)}>"  # noqa

    def __rich__(self):
        return f"<[green]typed c[/green] pointer to [cyan]{str(self)}[/cyan]>"  # noqa

    def __del__(self):
        if (self.type is not str) and (self._decref):
            super().__del__()
            remove_ref(~self)


class TypedCPointer(_TypedPointer[T]):
    """Class representing a pointer with a known type."""

    @property
    def _as_parameter_(self) -> "ctypes.pointer[ctypes._CData]":
        ctype = self.get_mapped(self.type)
        deref = ctype.from_address(self.ensure())
        return ctypes.pointer(deref)

    def dereference(self) -> T:
        """Dereference the pointer."""
        ctype = self.get_mapped(self.type)

        if ctype is ctypes.c_char_p:
            return ctypes.c_char_p(self.ensure()).value  # type: ignore

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

    def __invert__(self) -> T:
        """Dereference the pointer."""
        return self.dereference()


class CArrayPointer(_TypedPointer[T], Generic[T]):
    """Class representing a pointer with a known type."""

    def __init__(
        self,
        address: int,
        data_type: Type[T],
        length: int,
        size: int,
        void_p: bool = False,
        decref: bool = True,
    ):
        self._length = length
        super().__init__(address, data_type, size, void_p, decref)

    @property
    def _as_parameter_(self) -> "ctypes.Array[ctypes._CData]":
        ctype = self.get_mapped(self.type)

        deref = (ctype * self._length).from_address(self.ensure())
        return deref

    def dereference(self) -> List[T]:
        """Dereference the pointer."""
        array = self._as_parameter_
        return [array[i] for i in range(self._length)]  # type: ignore

    def __repr__(self) -> str:
        return f"<c array pointer to {str(self)}>"  # noqa

    def __rich__(self):
        return f"<[green]typed c[/green] pointer to [cyan]{str(self)}[/cyan]>"  # noqa

    def __getitem__(self, index: int) -> T:
        array = ~self
        return array[index]

    def __iter__(self) -> Iterator[List[T]]:
        """Dereference the pointer."""
        return iter({self.dereference()})

    def __invert__(self) -> List[T]:
        """Dereference the pointer."""
        return self.dereference()


def cast(ptr: VoidPointer, data_type: Type[T]) -> TypedCPointer[T]:
    """Cast a void pointer to a typed pointer."""
    return TypedCPointer(
        ptr.ensure(),
        data_type,
        ptr.size,
        decref=False,
        void_p=True,
    )


def to_c_ptr(data: T) -> TypedCPointer[T]:
    """Convert a python type to a pointer to a C type."""
    ct = TypedCPointer.map_type(
        data,
    )

    add_ref(ct)
    address = ctypes.addressof(ct)
    typ = type(data)

    return TypedCPointer(address, typ, ctypes.sizeof(ct), False)


def to_struct_ptr(struct: A) -> StructPointer[A]:
    """Convert a struct to a pointer."""
    return StructPointer(id(struct), type(struct))


def array(*seq: T) -> CArrayPointer[List[T]]:
    f_type = type(seq[0])

    for i in seq:
        if type(i) is not f_type:  # dont use isinstance here
            raise ValueError(
                "all values in the array must be the same type",
            )

    length = len(seq)
    ctype = _BaseCPointer.get_mapped(f_type)
    arr = (ctype * length)(*seq)
    add_ref(arr)

    return CArrayPointer(  # type: ignore
        ctypes.addressof(arr),
        f_type,  # type: ignore
        length,
        ctypes.sizeof(ctype),
    )
