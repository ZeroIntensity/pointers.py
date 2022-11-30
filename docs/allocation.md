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

## Stack

Objects can be put on the stack using `stack_alloc` or `acquire_stack_alloc`:

```py
from pointers import stack_alloc, StackAllocatedPointer

@stack_alloc(28)
def test(ptr: StackAllocatedPointer):
    ptr <<= 1
    print(*ptr)

test()
```

The difference between `acquire_stack_alloc` and `stack_alloc` is that `acquire_stack_alloc` automatically calls the function, whereas `stack_alloc` makes you call it manually:

```py
from pointers import stack_alloc, acquire_stack_alloc, StackAllocatedPointer

@stack_alloc(28)
def a(ptr: StackAllocatedPointer):  # you need to call a manually
    ...

@acquire_stack_alloc(28)
def b(ptr: StackAllocatedPointer):  # this is called automatically by the decorator
    ...
```

Stack allocated pointers **cannot** be deallocated manually, meaning the following **will not** work:

```py
from pointers import acquire_stack_alloc, StackAllocatedPointer, free

@acquire_stack_alloc(28)
def test(ptr: StackAllocatedPointer):
    free(ptr)  # ValueError is raised
```

Instead, it will be popped off the stack at the end of the function. Read more about that below.

### Why not a context?

**Warning:** This section is for advanced users.

We have to go through a couple different reasons on why we need to use a decorator instead of a context for stack allocations.

First, we need to understand how functions are handled in ASM (at least on GNU compilers).

Lets take a look at this piece of x86 ASM as an example (32 bit):

```asm
global _start

_start:
    push 123 ; 123 on stack
    call func ; call our function
    mov eax, 1 ; system exit
    mov ebx, 0 ; return code
    int 0x80 ; call kernel

func:
    push ebp ; push base pointer onto the stack
    mov ebp, esp ; preserve current stack top

    mov esp, ebp
    pop ebp ; restore base pointer
    ret ; jump to return address
```

This function does nothing, but as you can see with the `push` and `pop` instructions, we are using the stack to pass parameters and store the return address of the functions.

When we put something on the top of the stack in Python, we still need to follow these rules. The memory is popped off the stack at the end of the C function (in this case, its pointers.py's `run_stack_callback`), so we cannot use it elsewhere.

Now, how does this relate to using a context or not?

Python context managers are done like this:

```py
class MyContext:
    def __enter__(self):
        ...

    def __exit__(self, *_):
        ...

with MyContext() as x:
    ...
```

Remember, the data is popped off the stack after the end of the C function, not the Python function, meaning we can't just allocate and then store in the class. We also can't just do it all from `__enter__`, since the allocated memory will be destroyed at the end of it.

We also can't do it from a C based class, since that will still have to return the object.

Note that there's also no yielding in C, so we can't return early either.
