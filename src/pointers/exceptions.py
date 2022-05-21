__all__ = ("IsMallocPointerError", "AllocationError", "NotEnoughChunks", "IsFrozenError", "DereferenceError")


class IsMallocPointerError(Exception):
    """Raised when trying perform an operation on a malloc pointer that isn't supported."""  # noqa

    pass


class AllocationError(Exception):
    """Raised when a memory allocation fails."""

    pass


class NotEnoughChunks(Exception):
    """Raised when there aren't enough chunks in a CallocPointer."""

    pass


class IsFrozenError(Exception):
    """Raised when trying to move the address of a frozen pointer."""

    pass


class DereferenceError(Exception):
    """Raised when trying to dereference an object address that doesn't exist."""  # noqa

    pass
