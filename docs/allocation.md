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

## Malloc Pointer

`MallocPointer` is extremely similar to `Pointer`, with a few differences:

- `freed` and `assigned` property are present.
- Attempting to read property `type` results in a `IsMallocPointerError`
- Pointer assignment unsupported (also results in a `IsMallocPointerError`)

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

## Calloc

`calloc` is a bit more complicated than `malloc` and `realloc`. Instead of allocating one block of memory, it allocates multiple blocks of a specified size.

Basic usage:

```py
from pointers import calloc

memory = calloc(3, 28)
memory <<= 5

print(~memory)
```

`calloc` also **does not** return a `MallocPointer` object. Instead, it returns its own `CallocPointer` object.

Now, to use the other allocated chunks, we can use pointer arithmetic.

```py
memory = calloc(4, 28)
memory <<= 1 # assigns first chunk to 1
memory += 1 # access next chunk
memory <<= 2 # assigns this chunk to 2
print(~memory)
```

If you attempt to skip more chunks than are allocated, a `NotEnoughChunks` error is raised:

```py
memory = calloc(1, 28)
memory += 2 # NotEnoughChunks: chunk index is 2, while allocation is 1
```

### Safe Mode

Due to garbage collection, segmentation faults are extremely common when using `calloc`. For example:

```py
from pointers import calloc

memory = calloc(4, 28)

for index, ptr in enumerate(memory):
    ptr <<= index + 1

for i in memory:
    print(~i) # segmentation fault occurs
```

Luckily, pointers.py has a fix for this. Pass `safe = True` when calling `calloc`:

```py
from pointers import calloc

memory = calloc(4, 28, safe = True)
memory <<= 1
memory += 1
memory <<= 2
memory -= 1
print(~memory) # this would normally cause a segmentation fault
```

Alternatively, you can use `calloc_safe`:

```py
from pointers import calloc_safe

memory = calloc_safe(4, 28) # same thing as passing safe = True
```

### What does safe do?

Safety with `calloc` enables value caching internally.

When safe is disabled, dereferencing the pointer will lookup the memory address stored in the pointer, so when it doesn't exist, a segmentation fault occurs.

Safe fixes this by storing the value in the pointer itself. While this breaks the "legacy" of this awful library, it's really the only way to allow `calloc` to work at all.

### Calloc Pointer

`CallocPointer` inherits from `MallocPointer`, so it's mostly the same, but has a few different features:

- `safe`, `chunks`, `chunk_size`, and `current_index` properties are present.
- Dereferencing using `*` is not supported
