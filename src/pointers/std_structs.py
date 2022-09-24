import ctypes
from typing import TYPE_CHECKING, Dict, Type

from ._cstd import div_t, lconv, ldiv_t, tm
from ._pyapi import PyType_Slot, PyType_Spec
from .structure import Struct, StructPointer

if TYPE_CHECKING:
    from .c_pointer import VoidPointer

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
    decimal_point: str
    thousands_sep: str
    grouping: str
    int_curr_symbol: str
    currency_symbol: str
    mon_decimal_point: str
    mon_thousands_sep: str
    mon_grouping: str
    positive_sign: str
    negative_sign: str
    frac_digits: str
    p_cs_precedes: str
    p_sep_by_space: str
    n_sep_by_space: str
    p_sign_posn: str
    n_sign_posn: str


class PyTypeSlot(Struct):
    slot: int
    pfunc: "VoidPointer"


class PyTypeSpec(Struct):
    name: bytes
    basic_size: int
    itemsize: int
    flags: int
    slots: StructPointer[PyTypeSlot]


STRUCT_MAP: Dict[Type[ctypes.Structure], Type[Struct]] = {
    tm: Tm,
    div_t: DivT,
    ldiv_t: LDivT,
    lconv: Lconv,
    PyType_Slot: PyTypeSlot,
    PyType_Spec: PyTypeSpec,
}
