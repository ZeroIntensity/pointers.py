import inspect
from contextlib import suppress
from functools import wraps
from typing import Any, Callable, Dict, Tuple, TypeVar, get_type_hints

from typing_extensions import Annotated, ParamSpec, get_args, get_origin

from .object_pointer import Pointer, to_ptr

T = TypeVar("T")
P = ParamSpec("P")

__all__ = ("decay", "decay_annotated", "decay_wrapped")


def _make_func_params(
    func: Callable[P, Any],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    hints = get_type_hints(func, include_extras=True)
    actual: dict = {}
    params = inspect.signature(func).parameters

    for index, key in enumerate(params):
        if key in kwargs:
            actual[key] = kwargs[key]
        else:
            with suppress(IndexError):
                actual[params[key].name] = args[index]

    return (hints, actual)


def _decay_params(
    func: Callable[..., Any],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    hints, actual = _make_func_params(func, args, kwargs)

    for key, value in hints.items():
        if (get_origin(value) is Pointer) or (value is Pointer):
            actual[key] = to_ptr(actual[key])

    return actual


def decay(func: Callable[P, T]) -> Callable[..., T]:
    """Automatically convert values to pointers when called."""

    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        actual = _decay_params(func, args, kwargs)
        return func(**actual)  # type: ignore

    return inner


def decay_annotated(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs):
        hints, actual = _make_func_params(func, args, kwargs)

        for param, hint in hints.items():
            if get_origin(hint) is not Annotated:
                continue

            hint_arg = get_args(hint)[1]

            if (hint_arg is Pointer) or (get_origin(hint_arg) is Pointer):
                actual[param] = to_ptr(actual[param])

        return func(**actual)  # type: ignore

    return wrapped


def decay_wrapped(wrapper: Callable[P, T]) -> Callable[..., Callable[P, T]]:
    def decorator(func: Callable[..., T]) -> Callable[P, T]:
        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs):
            actual = _decay_params(func, args, kwargs)
            return func(**actual)

        return wrapped

    return decorator  # type: ignore
