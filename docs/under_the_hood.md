# Under The Hood

**Warning:** This is for advanced readers.

This page goes into detail about how pointers.py works internally and different Python memory concepts.

## Python Memory

### Basics

If you found pointers.py from reddit or something similar, theres a good chance you've seen a comment like "everything in python is already a pointer".

This is true, but you might be thinking "no it's not, i don't have to dereference or get the address of anything".

Lets use the following as an example:

```py
a = 1
b = 1

print(id(a), id(b))
```

In CPython, `id` gets the address of the object. Executing this code will show that they are both the same address.

This is because both `a` and `b` are interally pointers to the same `PyObject`.

Think of variables looking something like this:

| Name            | Value                         |
| --------------- | ----------------------------- |
| `variable_name` | `PyObject* at 0x7ffb74bb16b0` |

Heres what a `PyObject` itself might look like:

| Type  | Value | Reference Count |
| ----- | ----- | --------------- |
| `int` | `1`   | `100`           |

### Garbage Collection

Python does garbage collection based off of [reference counting](https://en.wikipedia.org/wiki/Reference_counting).

This means that when an tracked object's reference count hits 0, the object is garbage collected.

We can use the following as an example:

```py
class test:
    pass

test()
```

This code is completely useless, and creating an instance of `test` is only going to take up memory.

Python realizes this, so when it sees that we have an instance of `test` that has no references, it destroys it and frees the memory.

## Pointer API

### Basics

#### Misconceptions

When some people see pointers.py for the first time, they assume that it works by simply holding the value internally and then returning it when dereferencing.

They expect the code to look something like the following:

```py
class Pointer(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def dereference() -> T:
        return self._value
```

**This is not at all how pointers.py works.**

#### How does it actually work?

Essentially, the `to_ptr` function takes in an object, and then uses this [CPython implementation detail](https://docs.python.org/3/library/functions.html#id) to get the address of that object.

It takes this address and then stores it in our pointer object. Then, when we call `dereference()`, we use either [ctypes](https://docs.python.org/3/library/ctypes.html) or [gc](https://docs.python.org/3/library/gc.html) to get the original object.

### Dereferencing

#### The Garbage Collector

Above, we said that we could use the [gc](https://docs.python.org/3/library/gc.html) module to dereference a pointer object.

Looking at this module's documentation, there isn't any clear way to do something like get an object by address, so how do we do it?

Lets go back to `to_ptr`:

```py
def to_ptr(val: T) -> Pointer[T]:
    """Convert a value to a pointer."""
    return Pointer(id(val), type(val), gc.is_tracked(val))
```

Above when we talked about the basics of how the pointer implementation works, I didn't talk about the `Pointer` objects other parameters, which are `type` and `tracked`.

`type` is fairly simple, as it's just the data type of what the pointer is looking at, but `tracked` is more complicated.

`tracked` is whether the pointer is tracked by the garbage collector. If this is `True`, then we use the `dereference_tracked` internal function to dereference.

If it's `False`, then we use `dereference_address`.

#### Difference between tracked and address

`dereference_address` will work on any object, but has one large flaw.

This function uses [ctypes](https://docs.python.org/3/library/ctypes.html), and simply attempts to read the `PyObject` at the specified address.

But if the address isn't valid (such as when the object is garbage collected), the Python interpreter is terminated with `SIGSEGV`.

```py
class test:
    pass

ptr = Pointer(id(test()), test, False)
print(~ptr) # since we set tracked to false, it uses dereference_address and causes a segfault
```

This was an issue in pointers.py for a while until version 1.2.5 introduced `dereference_tracked`.

`dereference_tracked` doesn't use C, and instead goes through the objects tracked by the garbage collector.

If an object matches, we return it.

```py
def dereference_tracked(address: int) -> Any:
    """Dereference an object tracked by the garbage collector."""
    for obj in gc.get_objects():
        if id(obj) == address:
            return obj

    raise DereferenceError(...)
```

Then, when calling `dereference()` on our original pointer, we simply check whether the target is tracked:

```py
def dereference(self) -> T:
    """Dereference the pointer."""
    return (dereference_tracked if self.tracked else dereference_address)(self.address)
```

### Movement

#### Basics

Lets look at the source for movement:

```py
def move(self, data: "Pointer[T]") -> None:
    """Move data from another pointer to this pointer. Very dangerous, use with caution.""" # noqa
    if data.type is not self.type:
        raise ValueError("pointer must be the same type")

    deref_a: T = ~data
    deref_b: T = ~self

    bytes_a = (ctypes.c_ubyte * sys.getsizeof(deref_a)) \
        .from_address(data.address)
    bytes_b = (ctypes.c_ubyte * sys.getsizeof(deref_b)) \
        .from_address(self.address)

    ctypes.memmove(bytes_b, bytes_a, len(bytes_a))
```

This looks like a mess at first, but is fairly simple.

We get the bytes for both pointers from their addresses using C.

Then, we use C's `memmove()` function to copy the bytes of the specified pointer to the current pointer.

#### Dangers

I specified some dangers in the [movement](movement.md) page, but we'll go more into depth here.

Lets use the following code as an example:

```py
import ctypes
import struct
import sys
from pointers import to_ptr

def print_data(val: int):
    data = ctypes.string_at(id(val), 28)
    ref_count, type_address, number_of_digits, lowest_digit = \
        struct.unpack('qqqi', data)

    print('reference count: ', ref_count, sys.getrefcount(x))
    print('type address:    ', type_address, id(type(x)))
    print('number of digits:', number_of_digits, -(-x.bit_length() // 30))
    print('lowest digit:    ', lowest_digit, x % 2**30)

x = 19
print_data(x)
print('----')

ptr = to_ptr(x)
ptr <<= 21

print_data(x)
```

This should give something like the output:

```
reference count:  16 18
type address:     9483264 9483264
number of digits: 1 1
lowest digit:     19 19
----
reference count:  15 16
type address:     9483264 9483264
number of digits: 1 1
lowest digit:     21 21
```

The lowest digit and reference count are overwritten when we move the data.

When we talked about the garbage collector above, I said how python did its garbage collection based on referencing counting.

If we overwrite the reference count, that means that python could fail to collect something or accidentally collect something too early (which will result in segfaults).

## Memory Functions

### Basics

The original implementations of `malloc` and `free` were added in version 1.1.2

Pointers.py supports memory management by using [ctypes](https://docs.python.org/3/library/ctypes.html).

If you look at the [\_cstd.py](https://github.com/ZeroIntensity/pointers.py/blob/master/src/pointers/_cstd.py) file, you can see the C functions loaded from the DLL and their signatures.

The basic implementation is simple:

```py
# not actual source code

def malloc(size: int) -> MallocPointer:
    address: int = c_malloc(size) # allocates from the cdll
    ... # create the pointer object with the address
```

### Movement

#### Basics

Movement is much safer in allocated memory, since we aren't overwriting anything.

In fact, we aren't even using `memmove`:

```py
def move(self, data: Pointer[T]) -> None:
    """Move data to the allocated memory."""
    if self.freed:
        raise FreedMemoryError("memory has been freed")

    bytes_a = (ctypes.c_ubyte * sys.getsizeof(~data)) \
        .from_address(data.address)

    ptr = self.make_ct_pointer()
    byte_stream = bytes(bytes_a)

    try:
        ptr.contents[:] = byte_stream
    except ValueError as e:
        ...
```

We make a ctypes pointer from the allocated memory, and use the same method as earlier to get the bytes of the new pointer.

Then, we sent the pointers contents to those bytes.

#### Safety

We have to use `ptr.contents[:]` to ensure that the bytes are the same size, and if it isn't then we throw an error:

```py
raise InvalidSizeError(
    f"object is of size {len(byte_stream)}, while memory allocation is {len(ptr.contents)}" # noqa
) from e
```

This is to make sure that we fill all the memory allocated. If we don't, we'll probably break things.

### Free and Realloc

#### Free

The `free` implementation is extremely simple:

```py
def free(target: MallocPointer):
    """Free allocated memory."""
    ct_ptr = target.make_ct_pointer()
    c_free(ct_ptr)
    target.freed = True
```

We make a ctypes pointer, call `free` from the DLL, and then set the `freed` property to `True` on the target pointer.

When `freed` is true, pointers.py won't let us dereference the memory.

#### Realloc

Once again, the implementation is very simple:

```py
def realloc(target: MallocPointer, size: int) -> None:
    """Resize a memory block created by malloc."""
    ct_ptr = target.make_ct_pointer()
    address: Optional[int] = c_realloc(ct_ptr, size)

    if not address:
        raise AllocationError("failed to resize memory")

    target.size = size
```

We once again make a ctypes pointer, and then call the memory function from the DLL.

Then, we just change the size of the passed object to allow more.

### Calloc

#### Basics

The `calloc` function itself is very simple, but the `CallocPointer` object that manages it is more complicated.

Lets start out with taking a look at `calloc`:

```py
def calloc(num: int, size: int) -> CallocPointer:
    """Allocate a number of blocks with a given size."""
    address: int = c_calloc(num, size)

    if not address:
        raise AllocationError("failed to allocate memory")

    return CallocPointer(address, num, size, 0)
```

When we return our `CallocPointer` object with the allocated memory, we pass a 0 at the end.

This 0 represents the current chunk accessed, which we will talk about next

#### Chunks

`malloc` allocates one chunk of memory with `x` size, whereas `calloc` allocates `x` chunks of `n` size.

In order to access each chunk, we need to get its address. Pointers.py does this by using the following:

```py
self.address + (amount * self.size)
```

Then, we get a new `CallocPointer` object with that address and return it to the user.

#### Zeroed Memory

Memory created by `calloc` in C is initalized to 0 by default.

That means that we can just dereference our `CallocPointer` immediately, right?

No, since a C 0 is not a `PyObject`. We can dereference it just fine, but we can't use it as a python object.

We can fix this, though.

pointers.py replicates zeroed memory by just moving a `PyObject` 0 to the memory when our `CallocPointer` is initalized:

```py
bytes_a = (ctypes.c_ubyte * 24) \
    .from_address(id(0))

ctypes.memmove(address, bytes_a, len(bytes_a))
```
