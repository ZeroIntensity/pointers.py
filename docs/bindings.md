# Bindings

Pointers.py provides Python bindings for C's memory functions:

```py
from pointers import py_malloc, py_realloc, py_calloc, py_free

memory = py_malloc(100)
memory = py_realloc(memory, 10)
py_free(memory)

array = py_calloc(1, 100)
py_free(memory)
```

If the allocation fails, an `AllocationError` is raised.

## Differences between bindings and normal functions

The raw `py_*` bindings are much lower lever than the normal binded functions.

These bindings don't even return a `Pointer` object.

Instead, they simply return the address of the newly allocated memory (apart from `py_free`, which returns `None`).

## Is there any benefit to using the raw bindings?

No. They exist in case you ever want to access C memory functions without having to deal with pointers.py's API.
