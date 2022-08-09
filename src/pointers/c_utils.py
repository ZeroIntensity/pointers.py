import ctypes
from typing import Any, Dict, Type, Union

from .exceptions import InvalidSizeError

__all__ = (
    "attempt_decode",
    "move_to_mem",
    "map_type",
    "get_mapped",
    "is_mappable",
    "get_py",
    "make_py",
)


def move_to_mem(
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


def map_type(data: Any) -> "ctypes._CData":
    """Map the specified data to a C type."""
    typ = get_mapped(type(data))
    return typ(data)


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


def is_mappable(typ: Any) -> bool:
    """Whether the specified type is mappable to C."""
    try:
        get_mapped(typ)
        return True
    except ValueError:
        return False


def get_py(
    data: Type["ctypes._CData"],
) -> Type[Any]:
    """Map the specified C type to a Python type."""
    from ._pointer import BasePointer

    if data.__name__.startswith("LP_"):
        return BasePointer

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

    try:
        return types[data]
    except KeyError as e:
        raise ValueError(
            f"{data} is not a valid ctypes type",
        ) from e


def make_py(data: "ctypes._CData"):
    """Convert the target C value to a Python object."""
    typ = get_py(type(data))
    res = typ(data)

    if typ is bytes:
        res = attempt_decode(res)

    return res
