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

If you give an invalid size, then an `InvalidSizeError` is raised.

### Identity checking

Pointers.py has an known issue with identity checking when using `malloc` or `calloc`

Lets take the following code as an example:

```py
from pointers import malloc, free

mem = malloc(28)
mem <<= 1

assert ~mem is 1 # raises an AssertionError
free(mem)
```

**What's happening here?** Lets print out the memory addresses of `~mem` and `1`:

```py
mem = malloc(28)
mem <<= 1

print(id(~mem), id(1))
```

In my case, this returns `26493552 9788992`, even though the address for `1` should always be the same.

This means that the `is` operator will not work when dereferencing.

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

It also sets the allocated memory to zero, so you can dereference it immediately.

Basic usage:

```py
from pointers import calloc

memory = calloc(3, 28)
print(~memory) # 0
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

In older versions of pointers.py, the way `calloc` worked internally was broken. In these versions, the `calloc_safe` function needed to be used to get it working properly.

```py
from pointers import calloc_safe

mem = calloc_safe(4, 28)

for index, ptr in enumerate(mem):
    ptr <<= index + 1

print(' '.join([~i for i in mem])) # without calloc_safe, this used to cause a segfault
```

`calloc_safe` **did not** use pointers and was holding a dictionary containing values to prevent segfaults.

Since 1.2.4, this issue has been patched. For more information on what happened with the broken implementation, see the [GitHub issue](https://github.com/ZeroIntensity/pointers.py/issues/11).

### Calloc Pointer

`CallocPointer` inherits from `MallocPointer`, so it's mostly the same, but has a few different features:

- `safe`, `chunks`, `chunk_size`, and `current_index` properties are present.
- Dereferencing using `*` is not supported
