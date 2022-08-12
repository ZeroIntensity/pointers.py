# Getting Started

## Installation

To get started with pointers.py, install the library:

### Linux/macOS

```
$ python3 -m pip install -U pointers.py
```

### Windows

```
$ py -3 -m pip install -U pointers.py
```

### From Source

```
$ git clone https://github.com/ZeroIntensity/pointers.py && cd pointers.py
$ pip install .
```

**CPython 3.6+ is required**

Now, to ensure everything is working properly we can run this simple program:

```py
from pointers import to_ptr

ptr = to_ptr("hello world")
print(*ptr)
```

Running this should print `hello world` into the console.
