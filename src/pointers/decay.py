import inspect
from functools import wraps
from typing import get_type_hints, Callable, TypeVar
from typing_extensions import ParamSpec
from contextlib import suppress
from .pointer import to_ptr, Pointer
from .frozen_pointer import to_const_ptr, FrozenPointer

T = TypeVar("T")
P = ParamSpec("P")

__all__ = ("decay",)


def decay(func: Callable[P, T]) -> Callable[..., T]:
    """Automatically convert values to pointers when called."""

    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        hints = get_type_hints(func)
        actual: dict = {}
        params = inspect.signature(func).parameters

        # mypy is giving false positives here since it doesn't know how to
        # handle paramspec
        for index, key in enumerate(params):
            if key in kwargs:  # type: ignore
                actual[key] = kwargs[key]  # type: ignore
            else:
                with suppress(IndexError):
                    actual[params[key].name] = args[index]  # type: ignore

        for key, value in hints.items():
            if hasattr(value, "__origin__"):
                origin = value.__origin__

                if origin not in {Pointer, FrozenPointer}:
                    continue

                actual[key] = to_ptr(actual[key]) if origin is Pointer \
                    else to_const_ptr(actual[key])

        return func(**actual)  # type: ignore

    return inner
