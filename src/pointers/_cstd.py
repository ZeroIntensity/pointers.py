import ctypes
import os

__all__ = (
    "c_malloc",
    "c_free",
    "c_realloc",
    "c_calloc"
)

dll = ctypes.CDLL(
    "msvcrt" if os.name == "nt" else "libc.so.6"
    if os.name == "posix" else "libc.dylib"
)

# void* malloc(size_t size);
dll.malloc.argtypes = (ctypes.c_size_t,)
dll.malloc.restype = ctypes.c_void_p
# void free(void* ptr);
dll.free.argtypes = (ctypes.c_void_p,)
dll.free.restype = None
# void* realloc(void* ptr, size_t size);
dll.realloc.argtypes = (ctypes.c_void_p, ctypes.c_size_t)
dll.realloc.restype = ctypes.c_void_p
# void* calloc (size_t num, size_t size);
dll.calloc.argtypes = (ctypes.c_size_t, ctypes.c_size_t)
dll.calloc.restype = ctypes.c_void_p

c_malloc = dll.malloc
c_free = dll.free
c_realloc = dll.realloc
c_calloc = dll.calloc
