# flake8: noqa
from typing import Any, Callable, TypeVar

T = TypeVar("T")

def handle(
    func: Callable[..., T],
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> T: ...

class SegvError(Exception): ...
