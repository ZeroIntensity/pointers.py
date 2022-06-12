# Using Pointers

## Dereferencing

Ok, we know how to create pointers, but they aren't very useful if we only have pointer objects.

Pointers.py has a few different ways to dereference a pointer object. The simplest one is the `Pointer.dereference()` method:

```py
from pointers import Pointer, decay

@decay
def test(ptr: Pointer[str])
    print(ptr.dereference()) # prints "abc"

test("abc")
```

Unfortunately, calling dereference takes a _minimum_ of 15 characters, which can get messy very quickly.

The recommended way to dereference a pointer object is to use the `~` operator, which looks a lot nicer:

```py
@decay
def test(ptr: Pointer[str])
    print(~ptr) # much shorter and easier to type
```

Finally, you can use the `*` operator, like in low level languages:

```py
@decay
def test(ptr: Pointer[str])
    print(*ptr) # works the same as above
```

### Why should I use `~` over `*`?

The `~` operator is a **unary operator**, opposed to `*` which is for iterators.

This can cause some issues. For example:

```py
@decay
def test(ptr: Pointer[str])
    deref = ~ptr # valid, runs correctly
    deref = *ptr # invalid syntax error!

test("abc")
```

The `*` can also cause issues with iterability of the dereferenced object.

For example, if we have a `list` that we are trying to pass into a function, using the `*` operator steals the iterability:

```py
@decay
def test(ptr: Pointer[list])
    some_func(*ptr) # this only dereferences it, doesn't splat it
    some_func(**ptr) # this is treated as a kwarg splat, raises a typeerror

test([1, 2, 3])
```

### Dereference Errors

Dereferencing can fail for a number of reasons, the most common being garbage collection.

Lets take the following code as an example:

```py
from pointers import to_ptr

class test:
    pass

ptr = to_ptr(test())

print(~ptr) # this causes a DereferenceError, since python collects our instance before this
```

CPython does garbage collection based on reference counting, so you can stop the garbage collection by creating an instance variable, like so:

```py
instance = test() # this adds to the reference count and stops the collection
ptr = to_ptr(instance)

print(~ptr) # works just fine, no error
```

However, some types (such as `str` or `int`) are not tracked by the garbage collection, so you don't have to worry about them getting collected.

You can check if the object is tracked by reading the `Pointer.tracked` property:

```py
ptr = to_ptr(test())
ptr_2 = to_ptr("a")

print(ptr.tracked, ptr_2.tracked) # True False
```

### Segmentation Faults

A segmentation fault occurs when we try to access restricted memory.

This can occur for multiple reasons, but we'll use the following as an example:

```py
from pointers import dereference_address # internal function used by pointers.py

dereference_address(1)
```

Executing this code results in something like the following:

```
Fatal Python error: Segmentation fault

Current thread 0x00007fb99bffa740 (most recent call first):
  File "[omitted]", line 38 in dereference_address
[1]    424 segmentation fault
```

#### What's happening?

`dereference_address` attempts to read the `PyObject` at address 1, which isn't accessible by Python.

This results in the operating system terminating our program using signal `SIGSEGV`, and the [faulthandler](https://docs.python.org/3/library/faulthandler.html) module displays the traceback.

## Assignment

If we would like to switch where a pointer is pointing to, we can use the `assign` method:

```py
from pointers import to_ptr

a = to_ptr("a")
b = to_ptr("b")

a.assign(b)
print(~a) # prints "b", since a is now pointing to the address of b
```

Note that this **does not** change the original value, it only changes what the pointer is looking at.

If you would like to change the original value, please see [movement](movement.md).

### Operator

The `>>` operator can be used instead of calling `assign` manually as well:

```py
from pointers import to_ptr

a = to_ptr("a")
b = to_ptr("b")

a >>= b # does the same thing as above
```

In fact, we don't even need to create a second pointer when using `>>`.

```py
from pointers import to_ptr

a = to_ptr("a")
a >>= "b" # works just fine
```

### For C/C++ developers

Pointer assignment is simply just changing what a pointer is looking at. Example:

```cpp
int main() {
    int a = 0; // using an int instead of string
    int b = 0;

    int* ptr = &a;
    ptr = &b; // switches where the pointer is pointing to
    return 0;
}
```

## Frozen Pointers

If you don't want your pointer to ever change, you can use `FrozenPointer` and `to_const_ptr`:

```py
from pointers import to_const_ptr, FrozenPointer

ptr: FrozenPointer[str] = to_const_ptr("abc")
ptr >>= "123" # pointers.IsFrozenError
```

You can also use it with `decay`:

```py
from pointers import decay, FrozenPointer

@decay
def test(ptr: Pointer[str], ptr2: FrozenPointer[str]):
    ptr >>= "123" # works just fine
    ptr2 >>= "123" # pointers.IsFrozenError

test("a", "b")
```

## Inheritance of Object behaviour

Pointers will inherit specific behaviours from the PyObject it points to. This can be
pretty useful when it comes to delayed computations or JIT-like behaviour:

### Item Subscription

The Pointer will inherit the behaviour for item retrieval from the referenced PyObject,
as such, the Pointer can be subscripted as a downstream behaviour at computation:

```py
import numpy as np
from pointers import to_ptr

x = np.arange(100).reshape(4, 25)
v = to_ptr(x)

>> v[(0, 4)]
>> 3 # does the same thing as above
```

### Item Assignment

The Pointer will respect the item assignment methods as well:

```py
import numpy as np
from pointers import to_ptr

x = np.arange(100).reshape(4, 25)
>> x[0]
>> array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
       17, 18, 19, 20, 21, 22, 23, 24])

v = to_ptr(x)
v[(0, 4)] = 2

>> v[0]
>> array([ 0,  1,  2,  3,  2,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
       17, 18, 19, 20, 21, 22, 23, 24]) # the pointer value has changed
>> x[0]
>> array([ 0,  1,  2,  3,  2,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
       17, 18, 19, 20, 21, 22, 23, 24]) # the same for the original PyObject
```

### Caveats

Item subscription and assignment is only inherited by Pointer and Malloc Pointers,
attempting to reference a CallocPointer as such will return:

```py
from pointers import calloc

c = calloc(2, 120)
c << ['a', 'b', 'c']
c[0] = 5
>> TypeError: 'CallocPointer' object does not support item assignment
```

Instead, it is proper form to create an object directly, and reference the object itself.
Note though, that the Calloc chunk will only respect assignment if the object's size
is equal to or lesser than the original chunk + the reassigned object:

```py
from pointers import calloc

c = calloc(2, 120)
obj = ['a', 'b', 'c']
c << obj
obj[0] = 5

>> c.dereference()
>> [5, 'b', 'c']
```
