from ._cstd import c_malloc, c_calloc, c_realloc, c_free
from .exceptions import AllocationError
from typing import Callable

__all__ = ("py_malloc", "py_calloc", "py_realloc", "py_free")


def _base_binding(
    allocator: Callable, *args, message: str = "failed to allocate memory"
) -> int:
    memory = allocator(*args)

    if not memory:
        raise AllocationError(message)

    return memory


def py_malloc(size: int):
    """Binding for the malloc function."""
    return _base_binding(c_malloc, size)


def py_calloc(chunks: int, size: int):
    """Binding for the calloc function."""
    return _base_binding(c_calloc, chunks, size)


def py_realloc(address: int, size: int) -> int:
    """Binding for the realloc function."""
    return _base_binding(
        c_realloc,
        address,
        size,
        message="failed to resize memory",
    )


def py_free(address: int) -> None:
    """Binding for the free function."""
    c_free(address)
