import ctypes
from contextlib import suppress
from typing import Any, Optional, Type, TypeVar, Union, get_type_hints

from ._utils import attempt_decode, get_mapped
from .c_pointer import BaseCPointer
from .constants import RawType
from .object_pointer import Pointer

T = TypeVar("T", bound="Struct")

__all__ = (
    "Struct",
    "StructPointer",
)


def _get_type(
    class_: Type["Struct"],
    ct: Type["ctypes._CData"],
    name: str,
) -> Type["ctypes._CData"]:
    attr = getattr(class_, name, None)

    if isinstance(attr, RawType):
        return attr.tp

    return ct


class Struct:
    """Abstract class representing a struct."""

    def __init__(self, *args: Any, do_sync: bool = True):
        class_typ: Type[Struct] = type(self)

        if class_typ is Struct:
            raise Exception(
                "cannot instantiate Struct directly",
            )

        hints = get_type_hints(class_typ)
        self._hints = hints

        class _InternalStruct(ctypes.Structure):
            _fields_ = [
                (
                    name,
                    _get_type(class_typ, get_mapped(typ), name),
                )
                for name, typ in hints.items()  # fmt: off
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
        return f"<struct {type(self).__name__} at {hex(ctypes.addressof(self._struct))}>"  # noqa

    @property
    def struct(self) -> ctypes.Structure:
        """Raw internal Structure object."""
        return self._struct


class StructPointer(Pointer[T]):
    """Class representing a pointer to a struct."""

    def __init__(
        self,
        address: int,
        data_type: Type[T],
        existing: Optional["Struct"] = None,
    ):
        self._existing = existing
        super().__init__(address, data_type, True)

    @property
    def _as_parameter_(
        self,
    ) -> Union[int, "ctypes._PointerLike"]:
        existing = self._existing

        if existing:
            return ctypes.pointer(existing.struct)

        return self.ensure()

    def __repr__(self) -> str:
        return f"<pointer to struct at {str(self)}>"

    def __rich__(self) -> str:
        return f"<[bold blue]pointer[/] to struct at {str(self)}>"
