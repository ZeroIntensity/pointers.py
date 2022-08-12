# Allocation

## Basics

We can use memory functions (`malloc`, `free`, `calloc`, `realloc`) the same way you would use them in C, and use them via the pointer API.

Here's an example:

```py
from pointers import malloc, free

ptr = malloc(28)  # 28 is the size of integers larger than 0
free(ptr)
```

We can dereference the same way we did earlier, but first, we need to actually put something in the memory. We can do this via data movement:

```py
from pointers import malloc, free

ptr = malloc(28)
ptr <<= 1
print(*ptr)
free(ptr)
```

Data movement is much safer when using memory allocation, since we aren't actually overwriting memory tracked by Python.

We also aren't overwriting any existing objects, we are just putting the object into a memory space.

Here's a quick example:

```py
from pointers import malloc, free

ptr = malloc(28)
ptr <<= 1
print(*ptr)
ptr <<= 2
print(*ptr, 1) # prints out "2 1", since we dont have to overwrite the 1 object itself!
free(ptr)
```

We can bypass size limits the same way as before, but again, this is extremely discouraged. Instead, we should use `realloc`.

## Reallocation

The `realloc` function works a bit differently in pointers.py. We don't reassign the pointer like you would in C:

```py
ptr = realloc(ptr, 28)
```

Instead, we can just call `realloc` on the object directly, like so:

```py
from pointers import malloc, realloc, free

ptr = malloc(24)
ptr <<= 0
realloc(ptr, 28)
free(ptr)
```

## Identity

Identity of objects in CPython are defined by their memory address, so using `is` on objects inside allocated memory won't work properly:

```py
from pointers import malloc, free
import sys

text: str = "hello world"
ptr = malloc(sys.getsizeof(text))
ptr <<= text
print(~ptr is text)  # False
```

## Arrays

We can allocate an array using `calloc`:

```py
from pointers import calloc, free

ptr = calloc(4, 28)  # allocate an array of 4 slots of size 28
```

You can (somewhat) use an allocated array as you would in C:

```py
from pointers import calloc, free

array = calloc(4, 28)

for index, ptr in enumerate(array):
    ptr <<= index

print(ptr[1])  # prints out "1"
```
