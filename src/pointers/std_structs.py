import ctypes
from typing import Dict, Type

from ._cstd import div_t, lconv, ldiv_t, tm
from ._pyapi import (
    Py_buffer, Py_tss_t, PyCodeObject, PyFrameObject, PyInterpreterState,
    PyModuleDef, PyThreadState, PyType_Slot, PyType_Spec, PyTypeObject,
    PyVarObject
)
from .c_pointer import TypedCPointer, VoidPointer
from .structure import Struct, StructPointer
from .util import raw_type

__all__ = (
    "Tm",
    "DivT",
    "LDivT",
    "Lconv",
    "PyTypeSlot",
    "PyTypeSpec",
    "Buffer",
    "TypeObject",
    "ThreadState",
    "FrameObject",
    "VarObject",
    "ModuleDef",
    "TssT",
    "InterpreterState",
    "CodeObject",
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


class Buffer(Struct):
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


class TypeObject(Struct):
    pass


class ThreadState(Struct):
    pass


class FrameObject(Struct):
    __PYOBJECT__ = True


class VarObject(Struct):
    ob_size: int = raw_type(ctypes.c_ssize_t)
    ob_refcnt: int = raw_type(ctypes.c_ssize_t)
    ob_type: StructPointer[TypeObject]


class ModuleDef(Struct):
    m_base: bytes
    pfunc: VoidPointer


class TssT(Struct):
    pass


class InterpreterState(Struct):
    pass


class CodeObject(Struct):
    pass


STRUCT_MAP: Dict[Type[ctypes.Structure], Type[Struct]] = {
    tm: Tm,
    div_t: DivT,
    ldiv_t: LDivT,
    lconv: Lconv,
    PyType_Slot: PyTypeSlot,
    PyType_Spec: PyTypeSpec,
    Py_buffer: Buffer,
    PyInterpreterState: InterpreterState,
    PyModuleDef: ModuleDef,
    Py_tss_t: TssT,
    PyVarObject: VarObject,
    PyFrameObject: FrameObject,
    PyThreadState: ThreadState,
    PyTypeObject: TypeObject,
    PyCodeObject: CodeObject,
}
