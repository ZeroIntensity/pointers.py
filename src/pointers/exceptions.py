__all__ = (
    "IsMallocPointerError",
    "AllocationError",
    "NotEnoughChunks",
    "IsFrozenError",
    "DereferenceError",
    "FreedMemoryError",
    "InvalidSizeError",
    "InvalidBindingParameter",
    "NullPointerError",
)


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
    """Raised when dereferencing an address fails."""  # noqa

    pass


class FreedMemoryError(Exception):
    """Raised when trying to perform an operation on freed memory."""

    pass


class InvalidSizeError(Exception):
    """Raised when trying to move an object of the wrong size to an allocation."""  # noqa

    pass


class InvalidBindingParameter(Exception):
    """Raised when an invalid type is passed to the"""

    pass


class NullPointerError(Exception):
    """Raised when a pointer is null."""

    pass
