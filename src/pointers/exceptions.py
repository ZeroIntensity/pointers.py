__all__ = ("IsMallocPointerError",
           "AllocationError",
           "NotEnoughChunks",
           "IsFrozenError",
           "DereferenceError",
           "IncorrectItemExpectedForSubscriptError",
           "NotSubscriptableError",
           "CallocSubscriptionDangerError",
           "ImmutableObjectError")  # noqa


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


class IncorrectItemExpectedForSubscriptError(Exception):
    """Raised when an item subscript method is subscripted with a non-integer value."""  # noqa

    pass


class NotSubscriptableError(Exception):
    """Raised when a Pointer subscript is attempted to a PyObject that is not subscriptable."""  # noqa

    pass


class CallocInheritanceError(Exception):
    """Raised when attempting to subscript a Calloc chunk. Assignment like this is dangerous at this time."""  # noqa

    pass


class ImmutableObjectError(Exception):
    """Raised when attempting to setting item assignment to immutable objects."""  # noqa

    pass

class  MethodNotInheritedError(Exception):
    """Raised when attempting to use a method not inherited by the Pointer."""
    pass
