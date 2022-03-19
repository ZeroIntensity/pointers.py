# Allocation

## Malloc

If you are familiar with C, then you be familiar with the `malloc` function.

You can use this in pointers.py, like so:

```py
from pointers import malloc, MallocPointer

ptr: MallocPointer[str] = malloc(52) # we have to specify type manually
```

Instead of returning a `Pointer` object, `malloc` returns a `pointers.MallocPointer` object.

To assign data to the pointer, we have to use data movement:

```py
from pointers import malloc, MallocPointer

ptr: MallocPointer[str] = malloc(52)
ptr <<= "abc"
print(~ptr)
```

The size that we pass to `malloc` must match the data we move to the memory. In the example above, the string `"abc"` has a size of 52 bytes.

If you give an invalid size, then a `MemoryError` is raised.

## Free

To free the allocated memory from `malloc`, we must use `free`.

`free` is very simple. Just pass the `MallocPointer` object, and it will do the rest.

```py
from pointers import malloc, free

ptr = malloc(52)
ptr <<= "abc"
free(ptr) # frees the memory
```

A `MemoryError` is raised if you try to access the memory after it is freed.

## Malloc Pointer

`MallocPointer` is extremely similar to `Pointer`, with a few differences:

- `freed` and `assigned` property are present.
- Attempting to read property `type` results in a `IsMallocPointerError`
- Pointer assignment unsupported (also results in a `IsMallocPointerError`)
