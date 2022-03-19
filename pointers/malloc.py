import ctypes
import sys
from .pointer import Pointer
import os
from typing import TypeVar, Generic, Type, NoReturn

__all__ = (
    "IsMallocPointerError",
    "MallocPointer",
    "malloc",
    "free"
)

dll = ctypes.CDLL('msvcrt' if os.name == 'nt' else 'libc.dylib' if os.name == 'posix' else 'libc.so.6')

# void* malloc(size_t size);
dll.malloc.argtypes = ctypes.c_size_t,
dll.malloc.restype = ctypes.c_void_p
# void free(void* ptr);
dll.free.argtypes = ctypes.c_void_p,
dll.free.restype = None

T = TypeVar("T")

class IsMallocPointerError(Exception):
    """Raised when trying perform an operation on a malloc pointer that isn't supported."""
    pass

class MallocPointer(Pointer, Generic[T]):
    """Class representing a pointer created by malloc."""
    def __init__(self, address: int, size: int) -> None:
        self._address = address
        self._size = size
        self._freed = False
        self._assigned = False

    @property
    def freed(self) -> bool:
        """Whether the allocated memory has been freed."""
        return self._freed

    @freed.setter
    def freed(self, value: bool) -> None:
        self._freed = value

    @property
    def assigned(self) -> bool:
        """Whether the allocated memory has been assigned a value."""
        return self._assigned

    @assigned.setter
    def assigned(self, value: bool) -> None:
        self._assigned = value

    @property
    def type(self) -> NoReturn:
        """Type of the pointer."""
        raise IsMallocPointerError("malloc pointers do not have types")

    @property
    def size(self) -> int:
        """Size of the memory."""
        return self._size

    def assign(self, _) -> NoReturn:
        """Point to a different address."""
        raise IsMallocPointerError("cannot assign to malloc pointer")

    def __repr__(self) -> str:
        return f"<pointer to allocated memory at {hex(self.address)}>"

    def move(self, data: Pointer[T]) -> None:
        """Move data to the allocated memory."""
        if self.freed:
            raise MemoryError("memory has been freed")

        bytes_a = (ctypes.c_ubyte * sys.getsizeof(~data)).from_address(data.address)
        ptr = self.make_ct_pointer()
        byte_stream = bytes(bytes_a)

        try:
            ptr.contents[:] = byte_stream
        except ValueError as e:
            raise MemoryError(f"object is of size {len(byte_stream)}, while memory allocation is {len(ptr.contents)}") from e
        
        self.assigned = True

    def make_ct_pointer(self):
        return ctypes.cast(self.address, ctypes.POINTER(ctypes.c_char * self.size))

    def dereference(self):
        """Dereference the pointer."""
        if self.freed:
            raise MemoryError("memory has been freed")

        if not self.assigned:
            raise MemoryError("pointer has no value")

        return super().dereference()

def malloc(size: int) -> MallocPointer:
    """Allocate memory for a given size."""
    address = dll.malloc(size)
    return MallocPointer(address, size)

def free(target: MallocPointer):
    """Free allocated memory."""
    ct_ptr = target.make_ct_pointer()
    dll.free(ct_ptr)
    target.freed = True
