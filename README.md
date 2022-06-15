# pointers.py

![Tests](https://github.com/ZeroIntensity/pointers.py/actions/workflows/tests.yml/badge.svg)

## Bringing the hell of pointers to Python

Why would you ever need this

- [Documentation](https://pointerspy.netlify.app/)
- [Repository](https://github.com/ZeroIntensity/pointers.py)
- [PyPI](https://pypi.org/project/pointers.py)

### Example

```py
from pointers import to_ptr, Pointer, decay

a: str = '123'
b: str = 'abc'

@decay
def move(ptr_a: Pointer[str], ptr_b: Pointer[str]):
    ptr_a <<= ptr_b

move(a, b)
print(a, b) # abc abc
```

#### Example with bindings

```py
from pointers import fopen, fprintf, fclose

file = fopen("/dev/null", "w")
fprintf(file, "hello world")
fclose(file)
```

#### Example with malloc

```py
from pointers import malloc, free

memory = malloc(52)
memory <<= "abc"
print(*memory) # abc
free(memory)
print(*memory) # FreedMemoryError
```

### Why does this exist?

The main purpose of pointers.py is to simply break the rules of Python, but has some other use cases:

- Can help C/C++ developers get adjusted to Python
- Provides a nice learning environment for programmers learning how pointers work
- Makes it very easy to manipulate memory in Python
- Why _not_?

### Installation

#### Linux/macOS

```
python3 -m pip install -U pointers.py
```

#### Windows

```
py -3 -m pip install -U pointers.py
```

### Running Documentation

```
$ git clone https://github.com/ZeroIntensity/pointers.py && cd pointers.py
$ pip install -U mkdocs
$ mkdocs serve
```
