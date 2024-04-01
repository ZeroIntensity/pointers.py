import inspect
import warnings
from types import FrameType as Frame
from typing import Any, Dict, Optional, TypeVar, Union
from varname import nameof

from _pointers import force_update_locals

from .base_pointers import BasePointer
from .exceptions import NullPointerError, VariableLifetimeError
from .util import NULL, Nullable, handle

__all__ = "VarPointer", "to_var_ptr"

T = TypeVar("T")

class VarPointer(BasePointer[T]):
    def __init__(self, name: str, frame: Frame) -> None:
        self.name: Optional[str] = name
        self._frame = frame
        self._address = id(~self)

    def _get_scope(self) -> Dict[str, Any]:
        if not self.name:
            raise NullPointerError("pointer is NULL")

        frame = self._frame

        if self.name in frame.f_globals:
            return frame.f_globals

        if self.name in frame.f_locals:
            return frame.f_locals

        raise VariableLifetimeError(f'variable "{self.name}" no longer exists')

    @handle
    def move(
        self,
        target: Union[T, "BasePointer[T]"],
        *,
        unsafe: bool = False,
    ) -> None:
        if unsafe:
            warnings.warn("unsafe has no effect on variable pointers")

        if not self.name:
            raise NullPointerError("pointer is NULL")

        scope = self._get_scope()

        if (scope is self._frame.f_locals) and (
            self._frame.f_locals is not self._frame.f_globals
        ):
            force_update_locals(
                self._frame,
                self.name,
                (
                    ~target
                    if isinstance(
                        target,
                        BasePointer,
                    )
                    else target
                ),
            )
        else:
            scope[self.name] = (
                ~target
                if isinstance(
                    target,
                    BasePointer,
                )
                else target
            )

    @property
    def address(self) -> Optional[int]:
        return self._address

    def _cleanup(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"VarPointer(name={self.name!r})"

    def dereference(self) -> T:
        if not self.name:
            raise NullPointerError("pointer is NULL")

        return self._get_scope()[self.name]

    def assign(self, value: Nullable[Union["VarPointer[T]", T]], *, frame: int = 2) -> None:
        if value is NULL:
            self._address = 0
            self.name = None
            return

        fframe = inspect.currentframe()
        assert fframe
        assert fframe.f_back

        self.name = nameof(value, frame=frame)
        self._address = id(value)

    def __irshift__(
        self,
        value: Nullable[Union["VarPointer[T]", T]],
    ):
        self.assign(value, frame=3)
        return self


def to_var_ptr(value: T) -> VarPointer[T]:
    frame = inspect.currentframe()
    assert frame
    assert frame.f_back
    name = nameof(value, frame=2)
    return VarPointer(name, frame.f_back)
