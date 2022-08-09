# Welcome to pointers.py`s documentation!

## Bringing the hell of pointers to Python

-   [Source](https://github.com/ZeroIntensity/pointers.py)
-   [PyPI](https://pypi.org/project/pointers.py)

### Examples

```py
from pointers import Pointer, decay

a: str = '123'
b: str = 'abc'

@decay
def move(ptr_a: Pointer[str], ptr_b: Pointer[str]):
    ptr_a <<= ptr_b

move(a, b)
print(a, b) # abc abc
```

```py
from pointers import _

ptr = _&"hello world" # creates a new pointer object
assert _*ptr == "hello world"
```

```py
from pointers import fopen, fprintf, fclose

file = fopen("/dev/null", "w") # assigns to the c FILE* type
fprintf(file, "hello world")
fclose(file)
```

### What's new in 2.0.0?

-   Reworked documentation
-   Several bug fixes
-   Optimized internal API
-   Better type safety

### Features

-   Fully type safe
-   Pythonic pointer API
-   Bindings for the entire C standard library
-   Segfaults

### Why does this exist?

The main purpose of pointers.py is to simply break the rules of Python, but has some other use cases:

-   Can help translate C/C++ code into Python
-   Provides a nice learning environment for programmers learning how pointers work
-   Makes it very easy to manipulate memory in Python
-   Why _not_?
