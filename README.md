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

#### Creation

To convert something to a pointer, use the `pointers.to_ptr()` function. Then, when annotating function types use the `pointers.Pointer` class, like so:

```py
from pointers import Pointer, to_ptr

class test_class:
    pass

def some_function(ptr: Pointer[test_class]): # can be any data type (str, tuple, etc)
    ...

some_function(to_ptr(test_class())) # converts the instance to a pointer object
```

#### Dereferencing

To dereference a pointer, use the `Pointer.dereference()` function:

```py
def some_function(ptr: Pointer[test_class]):
    my_instance: test_class = ptr.dereference() # dereferences the pointer

instance = test_class()
some_function(to_ptr(instance))
```

Alternatively, you can use the \* operator to dereference the pointer:

```py
def some_function(ptr: Pointer[str]):
    print(*ptr) # a

some_function(to_ptr("a"))
```

Note that when using the \* operator, the following syntax will not work properly:

```py
deref = *ptr
print(deref)
```

For the above scenario you can use the dereferencing assignment operator, `,=`, or the `~` operator:

```py
deref ,= ptr # works correctly
print(deref)

deref = ~ptr # also works correctly
print(deref)
```

**A segmentation fault will occur if the address does not exist, so make sure the pointer is valid.**

#### Assignment

To assign the pointer to a different address, use the `assign()` method:

```py
ptr = to_ptr("abc")
ptr2 = to_ptr("test") # must be same type

ptr.assign(ptr2)
print(*ptr) # test
```

You can also use the `>>` operator instead, which gets rid of the need to pass in a pointer at all:

```py
ptr = to_ptr("abc")

ptr >> "test" # does not need to_ptr
print(*ptr) # test
```

#### Decaying

If you would like to automatically decay values to a pointer, use the `pointers.decay` decorator, like this:

```py
@decay
def some_function(ptr: Pointer[str], b: str): # converts "ptr" to a pointer since its hinted as Pointer[str]
    print(ptr.dereference(), b) # a b

some_function("a", "b") # converts "a" to a pointer, and leaves b as it is
```

Make sure you annotate the argument with `Pointer` or else decay won't convert it.
