# Bindings

**Warning:** This page assumes you are already familiar with the C programming language.

On top of the basic memory functions, pointers.py provides Python bindings for almost the entire C standard library.

To use one, simply import it:

```py
from pointers import strlen

print(strlen('hello')) # 5
```

Pointers.py will automatically convert the parameters to C values, and then convert the return value back to Python.

## Void Pointers

Some types (such as `FILE`) cannot be converted to Python. Pointers.py resolves this by returning a `VoidPointer` object.

```py
from pointers import fopen, fclose, fprintf

file = fopen('/dev/null', 'w')
fprintf(file, "hello")
fclose(file)
```

Although it won't be very useful, you can still dereference it:

```py
print(~file) # 4222428292
```

### Casting

If you need to cast a void pointer to a typed pointer, you can use the `cast` function, like so:

```py
from pointers import fopen, fclose, fprintf, cast

file = cast(fopen('/dev/null', 'w'), int) # type becomes TypedCPointer[int]
fprintf(file, "hello")
fclose(file)
```

### Typed vs void pointers

The `TypedCPointer` class inherits from `VoidPointer` so most of the behavior is the same, with 2 key differences:

- `VoidPointer` always points to `int`, whereas `TypedCPointer` always points to `T`.
- `TypedCPointer` forces the pointer to be the same type when using data movement, but `VoidPointer` will move any type.

## Structs

A few functions (such as `div`) return structs. Luckily, these are mappable to Python objects:

```py
from pointers import div

div(10, 1) # returns type DivT, which maps to the C struct div_t
```

In fact, you can even create your own structs:

```py
from pointers import Struct

class MyStruct(Struct):
    a: str
    b: str

a = MyStruct('a', 'b')
print(a.a) # a
```

### Struct Pointers

Functions such as `localeconv` return pointers to structs. These are mapped as `StructPointer` objects, which can be used like any other pointer:

```py
from pointers import localeconv

ptr = localeconv()
print((~ptr).grouping)
```

## Custom C Pointers

There might be a case where you need to make a pointer object to a C type. For this, you can use the `to_c_ptr` function:

```py
from pointers import to_c_ptr

ptr = to_c_ptr(1) # becomes TypedCPointer[int]
```

You can then use this pointer in any binding:

```py
from pointers import frexp, to_c_ptr

ptr = to_c_ptr(10)
print(frexp(8.0, ptr))
```

## Why to use these bindings?

The pointers.py bindings are must nicer to use opposed to something like `ctypes`:

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

Versatility and speed. The pointers.py bindings can make it harder to use your own functions with, as it forces you to use it's pointer API.

On top of that, the bindings are built on top of `ctypes`, which means that it cannot be faster. They also go through many type conversions in order to provide a nice API for the end user, which can slow things down significantly.
