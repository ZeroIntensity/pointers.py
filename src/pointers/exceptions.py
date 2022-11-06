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


class DereferenceError(Exception):
    """Raised when dereferencing an address fails."""  # noqa


class FreedMemoryError(Exception):
    """Raised when trying to perform an operation on freed memory."""


class InvalidSizeError(Exception):
    """Raised when trying to move an object of the wrong size to an allocation."""  # noqa


class InvalidBindingParameter(Exception):
    """Raised when an invalid type is passed to a binding."""


class NullPointerError(Exception):
    """Raised when a pointer is null."""


class InvalidVersionError(Exception):
    """Python version is not high enough."""


class SegmentViolation(Exception):
    """SIGSEGV was sent to Python."""
