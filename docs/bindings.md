# C Bindings

Pointers.py provides type safe bindings for most of the C standard library. We can use one by just importing it:

```py
from pointers import printf

printf("hello world\n")
```

## Collisions

Some names are either already used by python or used by pointers.py, so they are prefixed with `c_`.

For example, `raise` and `malloc` are both used, so you can import their bindings by importing `c_raise` and `c_malloc`:

```py
from pointers import c_raise, c_malloc

# ...
```

## Pointers

Several things in the C standard library require pointers. To create your own, you can use `to_c_ptr`:

```py
from pointers import to_c_ptr

ptr = to_c_ptr(1)  # creates a pointer to the c integer 1
```

Then, we can just pass it to the binding:

```py
from pointers import to_c_ptr, time

ptr = to_c_ptr(1)
time(ptr)
print(time)  # unix timestamp
```

### Strings

`to_c_ptr` automatically converts the passed type to a C type, but that can be misleading with strings.

When you pass a `str`, pointers.py has to convert it to a `wchar_t*`, not `char*`.

If you want a `char*`, you need to pass a `bytes` object:

```py
from pointers import to_c_ptr

wcharp = to_c_ptr("test")  # wchar_t*
charp = to_c_ptr(b"test")  # char*
```

This **is not** the same for the bindings though. Pointers.py is able to convert a `str` to `char*` just fine:

```py
from pointers import puts

puts("a")  # no need for a bytes object here
```

**Note:** Any pointer object that derives from `BaseCPointer` may be passed to a binding. Otherwise, you have to manually convert it.

## Void Pointers

Some types cannot be convert to a Python type or they can point to anything. For this, pointers.py uses the `VoidPointer` class:

```py
from pointers import c_malloc

ptr = c_malloc(0)  # ptr gets assigned to VoidPointer
```

`FILE*` is an example of a type that can't be converted:

```py
from pointers import fopen, fprintf, fclose

file = fopen("/dev/null", "w") # assigns to the c FILE* type
fprintf(file, "hello world")
fclose(file)
```

You can pass void pointers the same way:

```py
from pointers import c_malloc, printf

ptr = c_malloc(0)
printf("%p\n", ptr)
```

If you try and derefernce a void pointer, it just returns its memory address:

```py
from pointers import c_malloc

ptr = c_malloc(0)
print(*ptr)
```

### Casting

`VoidPointer` objects can be casted to a typed pointer with the `cast` function, like so:

```py
from pointers import c_malloc, printf, cast, strcpy, c_free

ptr = c_malloc(3)
strcpy(ptr, "hi")
printf("%s\n", cast(ptr, bytes))  # bytes refers to char*, str refers to wchar_t*
c_free(ptr)
```

You can even dereference a casted `VoidPointer` to get its actual value:

```py
ptr = c_malloc(3)
strcpy(ptr, "hi")
print(*cast(ptr, bytes))  # b'hi'
c_free(ptr)
```

## Structs

Some bindings, such as `div` return a struct. For this, pointers.py has its own `Struct` class:

```py
from pointers import div

a = div(10, 1)  # type is DivT, which inherits from Struct
print(a.quot)  # prints out 10
```

## Functions

There are a few bindings which require a function. All you have to do is write a function, and then pass it to the binding:

```py
from pointers import c_raise, signal, exit

def sighandler(signum: int):
    print(f"handling signal {signum}")
    exit(0)

signal(2, sighandler)
c_raise(2)  # send signal 2 to the program
```

## Custom Bindings

You can create your own binding to a C function with `ctypes` and pointers.py.

The recommended way to do it is via the `binds` function:

```py
from pointers import binds
import ctypes

dll = ctypes.CDLL("libc.so.6")  # c standard library for linux

# specifying the argtypes and restype isnt always required, but its recommended that you add it
dll.strlen.argtypes = (ctypes.c_char_p,)
dll.strlen.restype = ctypes.c_int

@binds(dll.strlen)
def strlen(text: str):
    ...
```

You can also use `binding`, but that isn't type safe:

```py
from pointers import binding
import ctypes

# ...

strlen = binding(dll.strlen)  # no type safety when calling strlen!
```

### Structs

We need to set the `restype` when returning a struct, so first you need to define a `ctypes.Structure` object:

```py
import ctypes

dll = ctypes.CDLL("libc.so.6")

class div_t(ctypes.Structure):
    _fields_ = [
        ("quot", ctypes.c_int),
        ("rem", ctypes.c_int),
    ]

dll.div.restype = div_t
```

Then, we need to create a pointers.py `Struct` that corresponds:

```py
from pointers import Struct

class DivT(Struct):
    quot: int
    rem: int
```

Then, we can finally define our binding:

```py
from pointers import binds, Struct
import ctypes

dll = ctypes.CDLL("libc.so.6")

class div_t(ctypes.Structure):
    _fields_ = [
        ("quot", ctypes.c_int),
        ("rem", ctypes.c_int),
    ]

class DivT(Struct):
    quot: int
    rem: int

dll.div.restype = div_t

@binds(dll.div, struct=DivT) # this tells pointers.py that this struct will be returned
def div(numer: int, denom: int) -> DivT:
    ...
```

## Why to use these bindings?

The pointers.py bindings are nicer to use opposed to something like `ctypes`:

_Comparison between `ctypes` and `pointers.py`_

```py
# ctypes

import ctypes

dll = ctypes.CDLL("libc.so.6") # this isn't cross platform, only works on linux
dll.strlen.argtypes = (ctypes.c_char_p,)
dll.strlen.restypes = ctypes.c_int

print(dll.strlen(b"hello")) # not type safe and requires bytes object
```

```py
# pointers.py

from pointers import strlen # this is cross platform

print(strlen("hello")) # type safe and doesnt force you to use bytes
```

## Why not to use these bindings?

Versatility and speed. The pointers.py bindings can make it harder to use your own functions with, as it forces you to use its pointer API.

On top of that, the bindings are built on top of `ctypes`, which means that it cannot be faster. They also go through many type conversions in order to provide a nice API for the end user, which can slow things down significantly.
