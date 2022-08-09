import inspect
from contextlib import suppress
from functools import wraps
from typing import Callable, TypeVar, get_type_hints

from typing_extensions import ParamSpec

from .object_pointer import Pointer, to_ptr

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

                if origin is not Pointer:
                    continue

                actual[key] = to_ptr(actual[key])

        return func(**actual)  # type: ignore

    return inner
