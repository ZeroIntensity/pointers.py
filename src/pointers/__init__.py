from .pointer import Pointer, decay, to_ptr, dereference_address
from .malloc import malloc, IsMallocPointerError, MallocPointer, free, realloc, AllocationError, calloc