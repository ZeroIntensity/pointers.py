from __future__ import annotations

import ctypes
import weakref
from abc import ABC, abstractmethod
from typing import Any, TypeVar, overload

from .base_pointer import Assignable, BasePointer, Movable
from .util import (
    Nullable, address_of, dec_ref_obj, inc_ref_obj, memory_handler
)

T = TypeVar("T")

__all__ = (
    "PyObjectPointer",
    "StrPointer",
    "IntPointer",
    "BoolPointer",
    "ObjectPointer",
    "to_ptr",
)


class PyObjectPointer(Assignable[T, T], Movable[T], BasePointer[T], ABC):
    """Base class for a pointer to a Python object."""

    def __init__(self, address: int) -> None:
        self.address = address
        self.is_null = address == 0
        self._unsafe = False
        if address:
            self.inc_ref()
        weakref.finalize(self, self._finalizer)

    def _finalizer(self):
        if not self.is_null:
            self.dec_ref()

    def assign(self, value: Nullable[T]) -> None:
        self.address = address_of(value)

    @abstractmethod
    def _move(self, value: T, *, safe: bool = False) -> None:
        ...

    @memory_handler
    def dereference(self) -> T:
        self._not_null()
        return ctypes.cast(self.address, ctypes.py_object).value

    @memory_handler
    def inc_ref(self) -> None:
        ctypes.pythonapi.Py_IncRef(~self)

    @memory_handler
    def dec_ref(self) -> None:
        ctypes.pythonapi.Py_DecRef(~self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.address})"


class StrPointer(PyObjectPointer[str]):
    def _move(self, value: str | StrPointer, *, safe: bool = True) -> None:
        print(safe)


class IntPointer(PyObjectPointer[int]):
    def _move(self, value: int | IntPointer, *, safe: bool = True) -> None:
        ...


class BoolPointer(PyObjectPointer[bool]):
    pass


class ObjectPointer(PyObjectPointer[T]):
    def _move(self, value: T | ObjectPointer, *, safe: bool = True):
        ...


_types: dict[type, type[PyObjectPointer[Any]]] = {
    str: StrPointer,
    int: IntPointer,
    bool: BoolPointer,
}


@overload
def to_ptr(obj: str) -> StrPointer:
    ...


@overload
def to_ptr(obj: int) -> IntPointer:
    ...


@overload
def to_ptr(obj: bool) -> BoolPointer:
    ...


@overload
def to_ptr(obj: T) -> ObjectPointer[T]:
    ...


def to_ptr(obj: T) -> PyObjectPointer[T]:
    tp = _types.get(type(obj))

    if tp:
        inc_ref_obj(obj)
        res = tp(id(obj))
        dec_ref_obj(obj)
        return res

    inc_ref_obj(obj)
    ptr = ObjectPointer(id(obj))
    dec_ref_obj(obj)
    return ptr
