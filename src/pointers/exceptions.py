__all__ = (
    "AllocationError",
    "DereferenceError",
    "FreedMemoryError",
    "InvalidSizeError",
    "InvalidBindingParameter",
    "NullPointerError",
    "InvalidVersionError",
    "SegmentViolation",
)


class AllocationError(Exception):
    """Raised when a memory allocation fails."""

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
    """Raised when an invalid type is passed to a binding."""

    pass


class NullPointerError(Exception):
    """Raised when a pointer is null."""

    pass


class InvalidVersionError(Exception):
    """Python version is not high enough."""

    pass


class SegmentViolation(Exception):
    """SIGSEGV was sent to Python."""

    pass
