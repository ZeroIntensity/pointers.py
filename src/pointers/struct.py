import ctypes
from typing import get_type_hints, Any
from abc import ABC
from .c_pointer import TypedCPointer, attempt_decode
from contextlib import suppress


class Struct(ABC):
    """Abstract class representing a struct values."""

    def __init__(self, *args, **kwargs):
        hints = get_type_hints(self.__class__)
        self._hints = hints

        class _InternalStruct(ctypes.Structure):
            _fields_ = [
                (name, TypedCPointer.get_mapped(typ)) for name, typ in hints.items()
            ]

        self._struct = _InternalStruct(*args, **kwargs)
        do_sync = kwargs.get("do_sync")

        if (kwargs.get("do_sync") is None) or (do_sync):
            self._sync()

    @property
    def _as_parameter_(self) -> ctypes.Structure:
        return self._struct

    @classmethod
    def from_existing(cls, struct: ctypes.Structure):
        instance = cls(do_sync=False)
        instance._struct = struct
        instance._sync()

        return instance

    def __getattribute__(self, name: str):
        attr = super().__getattribute__(name)

        with suppress(AttributeError):
            hints = super().__getattribute__("_hints")

            if (name in hints) and (type(attr)) is bytes:
                attr = attempt_decode(attr)

        return attr

    def __setattr__(self, name: str, value: Any):
        if hasattr(self, "_struct"):
            self._struct.__setattr__(name, value)
        super().__setattr__(name, value)

    def _sync(self):
        for name in self._hints:
            setattr(self, name, getattr(self._struct, name))

    def __repr__(self) -> str:
        return f"<struct {self.__class__.__name__} at {hex(ctypes.addressof(self._struct))}>"
