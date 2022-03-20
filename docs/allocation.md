# Allocation

## Malloc

If you are familiar with C, then you should be familiar with the `malloc` function.

You can use this in pointers.py, like so:

```py
from pointers import malloc, MallocPointer

ptr: MallocPointer[str] = malloc(52) # we have to specify type manually
```

**Note:** If the memory allocation fails, a `pointers.AllocationError` is raised.

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

## Realloc

If you need to change the size of the allocated memory, you can use `realloc`. Lets use the following code as an example:

```py
from pointers import malloc, free, realloc

ptr = malloc(52)
ptr <<= "abc"
realloc(ptr, 53) # allocates one more byte
ptr <<= "abcd" # works correctly
free(ptr)
```

**Note:** Like `malloc`, if the resize fails, `pointers.AllocationError` is raised.

Unlike in C, `realloc` in pointers.py **does not** return a pointer to the new memory. Instead, it simply allocates it and lets you use the old one.

## Malloc Pointer

`MallocPointer` is extremely similar to `Pointer`, with a few differences:

- `freed` and `assigned` property are present.
- Attempting to read property `type` results in a `IsMallocPointerError`
- Pointer assignment unsupported (also results in a `IsMallocPointerError`)
