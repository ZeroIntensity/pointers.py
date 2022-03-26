__all__ = ("IsMallocPointerError", "AllocationError", "NotEnoughChunks")


class IsMallocPointerError(Exception):
    """Raised when trying perform an operation on a malloc pointer that isn't supported."""  # noqa

    pass


class AllocationError(Exception):
    """Raised when a memory allocation fails."""

    pass


class NotEnoughChunks(Exception):
    """Raised when there aren't enough chunks in a CallocPointer."""

    pass
