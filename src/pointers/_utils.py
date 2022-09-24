import ctypes
from typing import Any, Dict, Type, Union

from _pointers import force_set_attr as _force_set_attr

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

_C_TYPES: Dict[Type[Any], Type["ctypes._CData"]] = {
    bytes: ctypes.c_char_p,
    str: ctypes.c_wchar_p,
    int: ctypes.c_int,
    float: ctypes.c_float,
    bool: ctypes.c_bool,
}

_PY_TYPES: Dict[Type["ctypes._CData"], type] = {
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
    ctypes.py_object: Any,  # type: ignore
}


def move_to_mem(
    ptr: "ctypes._PointerLike",
    stream: bytes,
    *,
    unsafe: bool = False,
    target: str = "memory allocation",
):
    """Move data to a C pointer."""

    slen = len(stream)
    plen = len(ptr.contents)  # type: ignore

    if (slen > plen) and (not unsafe):
        raise InvalidSizeError(
            f"object is of size {slen}, while {target} is {plen}",
        )

    ctypes.memmove(ptr, stream, slen)


def attempt_decode(data: bytes) -> Union[str, bytes]:
    """Attempt to decode a string of bytes."""
    try:
        return data.decode()
    except UnicodeDecodeError:
        return data


def map_type(data: Any) -> "ctypes._CData":
    """Map the specified data to a C type."""
    typ = get_mapped(type(data))
    return typ(data)  # type: ignore


def get_mapped(typ: Any) -> "Type[ctypes._CData]":
    """Get the C mapped value of the given type."""
    from .c_pointer import VoidPointer

    return {**_C_TYPES, VoidPointer: ctypes.c_void_p}.get(  # type: ignore
        typ,
    ) or ctypes.py_object


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
    from .base_pointers import BaseCPointer

    if data.__name__.startswith("LP_"):
        return BaseCPointer

    try:
        return _PY_TYPES[data]
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


def force_set_attr(typ: Type[Any], key: str, value: Any) -> None:
    """Force setting an attribute on the target type."""

    if not isinstance(typ, type):
        raise ValueError(
            f"{typ} does not derive from type (did you pass an instance and not a class)?",  # noqa
        )

    _force_set_attr(typ, key, value)


def deref(address: int) -> Any:
    """Get the value at the target address."""
    return ctypes.cast(address, ctypes.py_object).value
