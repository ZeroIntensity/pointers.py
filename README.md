# pointers.py

![Tests](https://github.com/ZeroIntensity/pointers.py/actions/workflows/tests.yml/badge.svg)

## Bringing the hell of pointers to Python

Why would you ever need this

-   [Documentation](https://pointerspy.netlify.app/)
-   [Source](https://github.com/ZeroIntensity/pointers.py)
-   [PyPI](https://pypi.org/project/pointers.py)

### Examples

```py
from pointers import _

text: str = "hello world"
ptr = _&text  # creates a new pointer object
ptr <<= "world hello"
print(text)  # world hello
```

```py
from pointers import c_malloc as malloc, c_free as free, strcpy, printf

ptr = malloc(3)
strcpy(ptr, "hi")
printf("%s\n", ptr)
free(ptr)
```

### Features

-   Fully type safe
-   Pythonic pointer API
-   Bindings for the entire C standard library
-   Segfaults

### Why does this exist?

The main purpose of pointers.py is to simply break the rules of Python, but has some other use cases:

-   Can help C/C++ developers get adjusted to Python
-   Provides a nice learning environment for programmers learning how pointers work
-   Makes it very easy to manipulate memory in Python
-   Why _not_?

### Installation

#### Linux/macOS

```
python3 -m pip install -U pointers.py
```

#### Windows

```
py -3 -m pip install -U pointers.py
```
