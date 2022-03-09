import ctypes
from typing import Generic, TypeVar, Any, Type
import gc

__all__ = (
    "DereferenceError",
    "dereference_address",
    "dereference_safe",
    "Pointer",
    "to_ptr",
    "NoAddressError"
)

T = TypeVar("T")
A = TypeVar("A")

class DereferenceError(Exception):
    """Raised when trying to dereference an address that does not exist."""
    pass

class NoAddressError(Exception):
    """Raised when trying to create a pointer to a value that has no address."""
    pass

def dereference_address(address: int) -> Any:
    """Dereference an address. Can cause a segmentation fault (to prevent, use `dereference_safe`)."""
    return ctypes.cast(address, ctypes.py_object).value

def dereference_safe(address: int) -> Any:
    """Safely dereference an address. Will not cause a segmentation fault."""
    for obj in gc.get_objects():
        if id(obj) == address:
            return obj
    raise DereferenceError(
        "address does not exist"
    )

class Pointer(Generic[T]):
    """Base class representing a pointer."""
    def __init__(self, address: int, typ: Type[T]) -> None:
        self._address = address
        self._type = typ
        
        if address not in [id(i) for i in gc.get_objects()]:
            raise NoAddressError(
                "address has already been dropped (perhaps you passed in a literal and not a variable?)"
            )

    @property
    def address(self):
        """Address of the pointer."""
        return self._address

    @property
    def type(self):
        """Type of the pointer."""
        return self._type

    def __repr__(self) -> str:
        return f"<pointer to {self.type.__name__} object at {hex(self.address)}>"

    def __str__(self) -> str:
        return hex(self.address)

    def dereference(self, safe: bool = True) -> T:
        """Dereference the pointer."""
        target = dereference_safe if safe else dereference_address
        return target(self.address)

def to_ptr(val: T) -> Pointer[T]:
    """Convert a value to a pointer."""

    return Pointer(id(val), type(val))