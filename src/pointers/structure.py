import ctypes
from contextlib import suppress
from typing import Any, List, Optional, Type, TypeVar, Union

from _pointers import add_ref

from ._utils import attempt_decode, get_mapped, get_py
from .base_pointers import BaseCPointer
from .c_pointer import TypedCPointer, VoidPointer
from .object_pointer import Pointer
from .util import RawType, handle

T = TypeVar("T", bound="Struct")

__all__ = (
    "Struct",
    "StructPointer",
)


class Struct:
    """Abstract class representing a struct."""

    def _convert_tc_ptr(self, typ: Any, name: str):
        if typ is TypedCPointer:
            raise TypeError(
                "cannot instantiate: TypedCPointer has no type argument",
            )

        if getattr(typ, "__origin__", None) is TypedCPointer:
            setattr(
                type(self),
                name,
                RawType(
                    ctypes.POINTER(get_mapped(typ.__args__[0])),
                ),
            )

        return typ

    def _get_type(
        self,
        ct: Type["ctypes._CData"],
        name: str,
    ) -> Type["ctypes._CData"]:
        attr = getattr(type(self), name, None)

        if isinstance(attr, RawType):
            return attr.tp

        if ct is ctypes.c_void_p:
            self._void_p.append(name)

        return ct

    def __init__(self, *args: Any, do_sync: bool = True):
        class_typ: Type[Struct] = type(self)

        if class_typ is Struct:
            raise Exception(
                "cannot instantiate Struct directly",
            )

        hints = class_typ.__annotations__
        self._void_p: List[str] = []
        self._hints = {k: self._convert_tc_ptr(v, k) for k, v in hints.items()}
        self._existing_address: Optional[int] = None

        class _InternalStruct(ctypes.Structure):
            _fields_ = [
                (
                    name,
                    self._get_type(get_mapped(typ), name),
                )
                for name, typ in self._hints.items()  # fmt: off
            ]

        self._struct = _InternalStruct(
            *[
                i if not isinstance(i, BaseCPointer) else i._as_parameter_
                for i in args  # fmt: off
            ]
        )

        if do_sync:
            self._sync()

    @property
    def _as_parameter_(self) -> ctypes.Structure:
        return self._struct

    @classmethod
    def from_existing(cls, struct: ctypes.Structure) -> "Struct":
        """Build a new struct from an existing ctypes structure.

        Args:
            struct: Existing `ctypes.Structure` object

        Returns:
            Created struct object.
        """
        instance = cls(do_sync=False)
        instance._struct = struct  # type: ignore
        # mypy is getting angry here for whatever reason
        instance._sync()
        instance._existing_address = ctypes.addressof(struct)

        return instance

    @handle
    def __getattribute__(self, name: str):
        attr = super().__getattribute__(name)

        with suppress(AttributeError):
            hints = super().__getattribute__("_hints")

            if (name in hints) and (type(attr)) is bytes:
                attr = attempt_decode(attr)

        if isinstance(attr, ctypes._Pointer):  # type: ignore
            value = attr.contents
            ct = type(value)

            if ct is ctypes.c_void_p:
                add_ref(ct)
                return VoidPointer(
                    ctypes.addressof(value),
                    ctypes.sizeof(value),
                )

            py_type = get_py(ct)
            return TypedCPointer(
                ctypes.addressof(value),
                py_type,
                ctypes.sizeof(value),
                False,
            )

        if name in super().__getattribute__("_void_p"):
            ct = ctypes.c_void_p(attr)  # type: ignore
            return VoidPointer(attr, ctypes.sizeof(ct))  # type: ignore

        return attr

    def __setattr__(self, name: str, value: Any):
        if hasattr(self, "_struct"):
            self._struct.__setattr__(name, value)
        super().__setattr__(name, value)

    def _sync(self) -> None:
        for name in self._hints:
            setattr(self, name, getattr(self._struct, name))

    def __repr__(self) -> str:
        return f"<struct {type(self).__name__} at {hex(ctypes.addressof(self._struct))}>"  # noqa

    @property
    def struct(self) -> ctypes.Structure:
        """Raw internal Structure object."""
        return self._struct

    def get_existing_address(self) -> int:
        if not self._existing_address:
            raise ValueError("instance has not been created from a C struct")
        return self._existing_address


class StructPointer(Pointer[T]):
    """Class representing a pointer to a struct."""

    def __init__(
        self,
        address: int,
        existing: Optional["Struct"] = None,
    ):
        self._existing = existing
        super().__init__(address, True)

    @property  # type: ignore
    @handle
    def _as_parameter_(
        self,
    ) -> Union[int, "ctypes._PointerLike"]:
        existing = self._existing

        if existing:
            return ctypes.pointer(existing.struct)

        return self.ensure()

    def __repr__(self) -> str:
        return (
            f"StructPointer(address={self.address}, existing={self._existing})"  # noqa
        )

    def __rich__(self) -> str:
        return f"<[bold blue]pointer[/] to struct at {str(self)}>"

    def get_existing_address(self) -> int:
        return (~self).get_existing_address()
