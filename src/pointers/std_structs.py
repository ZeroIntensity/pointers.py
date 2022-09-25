import ctypes
from typing import Dict, Type

from ._cstd import div_t, lconv, ldiv_t, tm
from ._pyapi import Py_buffer, PyType_Slot, PyType_Spec
from .c_pointer import TypedCPointer, VoidPointer
from .constants import raw_type
from .structure import Struct, StructPointer

__all__ = (
    "Tm",
    "DivT",
    "LDivT",
    "Lconv",
    "STRUCT_MAP",
)


class Tm(Struct):
    tm_sec: int
    tm_min: int
    tm_hour: int
    tm_mday: int
    tm_mon: int
    tm_year: int
    tm_wday: int
    tm_yday: int
    tm_isdst: int


class DivT(Struct):
    quot: int
    rem: int


class LDivT(DivT):
    pass


class Lconv(Struct):
    decimal_point: bytes
    thousands_sep: bytes
    grouping: bytes
    int_curr_symbol: bytes
    currency_symbol: bytes
    mon_decimal_point: bytes
    mon_thousands_sep: bytes
    mon_grouping: bytes
    positive_sign: bytes
    negative_sign: bytes
    frac_digits: bytes
    p_cs_precedes: bytes
    p_sep_by_space: bytes
    n_sep_by_space: bytes
    p_sign_posn: bytes
    n_sign_posn: bytes


class PyTypeSlot(Struct):
    slot: int
    pfunc: VoidPointer


class PyTypeSpec(Struct):
    name: bytes
    basic_size: int
    itemsize: int
    flags: int
    slots: StructPointer[PyTypeSlot]


class PyBuffer(Struct):
    buf: VoidPointer
    obj: VoidPointer
    len: int
    readonly: int
    itemsize: int
    format: bytes
    ndim: int
    shape: TypedCPointer[int] = raw_type(ctypes.POINTER(ctypes.c_ssize_t))
    strides: TypedCPointer[int] = raw_type(ctypes.POINTER(ctypes.c_ssize_t))
    suboffsets: TypedCPointer[int] = raw_type(ctypes.POINTER(ctypes.c_ssize_t))
    internal: VoidPointer


STRUCT_MAP: Dict[Type[ctypes.Structure], Type[Struct]] = {
    tm: Tm,
    div_t: DivT,
    ldiv_t: LDivT,
    lconv: Lconv,
    PyType_Slot: PyTypeSlot,
    PyType_Spec: PyTypeSpec,
    Py_buffer: PyBuffer,
}
