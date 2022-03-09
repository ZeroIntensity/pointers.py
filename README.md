# pointers.py

## Bringing the hell of pointers to Python

Why would you ever need this

### Example

```py
from pointers import Pointer, to_ptr

class test_class:
    pass

def some_function(ptr: Pointer[test_class]):
    print(repr(ptr)) # <pointer to test_class object at [address]>"

some_function(to_ptr(test_class()))
```

### Installation

#### Linux/macOS

```
python3 -m pip install -U pointers.py
```

#### Windows

```
py -3 -m pip install -U pointers.py
```

### Usage

To convert something to a pointer, use the `pointers.to_ptr()` function. Then, when annotating function types use the `pointers.Pointer` class, like so:

```py
from pointers import Pointer, to_ptr

class test_class:
    pass

def some_function(ptr: Pointer[test_class]): # can be any data type (str, tuple, etc)
    ...

some_function(to_ptr(test_class())) # converts the instance to a pointer object
```

To dereference a pointer, use the `Pointer.dereference()` function:

```py
def some_function(ptr: Pointer[test_class]):
    my_instance: test_class = ptr.dereference() # dereferences the pointer
```

If the pointer no longer exists, `pointers.DereferenceError` is raised.

You can add `safe = False` to the `Pointer.dereference()` function to use C when dereferencing. **A segmentation fault will occur if the address does not exist, so only use if you are sure the pointer is valid.**
