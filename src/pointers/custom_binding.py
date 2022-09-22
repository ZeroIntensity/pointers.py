import ctypes
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional, Type, TypeVar

from typing_extensions import ParamSpec

from .bindings import binding_base, make_string

if TYPE_CHECKING:
    from ctypes import _NamedFuncPointer

    from .structure import Struct

T = TypeVar("T")
P = ParamSpec("P")

__all__ = ("binds", "binding")


def binds(
    dll_func: "_NamedFuncPointer",
    *,
    struct: Optional[Type["Struct"]] = None,
):
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if kwargs:
                raise ValueError(
                    "keyword arguments are not allowed when calling C functions"  # noqa
                )

            restype = dll_func.restype

            if (
                struct
                and (not issubclass(restype, ctypes.Structure))  # type: ignore
                and (not (restype or int).__name__.startswith("LP_"))
            ):
                raise ValueError("restype must be a ctypes structure")

            return binding_base(
                dll_func,
                *[
                    # fmt: off
                    i if not isinstance(i, str)
                    else make_string(i)
                    # fmt: on
                    for i in args  # type: ignore
                ],
                map_extra={
                    dll_func.restype: struct,  # type: ignore
                }
                if struct
                else None,
            )

        return wrapper

    return decorator


def binding(
    dll_func: "_NamedFuncPointer",
    struct: Optional[Type["Struct"]] = None,
):
    @binds(dll_func, struct=struct)
    def wrapper(*args, **kwargs) -> Any:
        ...

    return wrapper
