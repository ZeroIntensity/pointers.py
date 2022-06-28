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

This is because both `a` and `b` are internally pointers to the same `PyObject`.

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

It takes this address and then stores it in our pointer object. Then, when we call `dereference()`, we use [ctypes](https://docs.python.org/3/library/ctypes.html) (or [gc](https://docs.python.org/3/library/gc.html) in versions prior to 1.3.3) to get the original object.

### Dereferencing

#### The Garbage Collector

In version 1.3.3, the `dereference_tracked` function was removed from pointers.py, along with the `Pointer.tracked` property.

`dereference_tracked` used the garbage collector to dereference its objects, and simply threw an exception if the object had been collected.

The following code used to be a classic example of how to raise a `DereferenceError`:

```py
from pointers import to_ptr

class Test:
    pass

ptr = to_ptr(Test()) # reference count hits 0 and this object is collected
print(~ptr) # DereferenceError!
```

But, now it works just fine.

Pointers.py does this by using the Python API itself to manually increase the reference count of pointer objects.

You can see this being done in `to_ptr`:

```py
def to_ptr(val: T) -> Pointer[T]:
    """Convert a value to a pointer."""
    add_ref(val)
    return Pointer(id(val), type(val))
```

The `increment_ref` parameter also exists when constructing a `Pointer` object, which will increment the reference count from `Pointer.__init__` in case you aren't instantiating from something like `to_ptr`.

The `add_ref` function refers to `_pointers.add_ref`, which is a C function that looks like this:

```c
static PyObject* method_add_ref(PyObject* self, PyObject* args) {
    Py_INCREF(args);
    Py_RETURN_NONE;
}
```

This manually adds to the objects reference count, and stops it from being collected while the pointer is in use.

We then can safely decrement the reference count when the pointer is deleted:

```py
def __del__(self):
    remove_ref(~self)
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
    ref_count, type_address, number_of_digits, lowest_digit = struct.unpack('qqqi', data)

    print('reference count: ', ref_count)
    print('type address:    ', type_address)
    print('number of digits:', number_of_digits)
    print('lowest digit:    ', lowest_digit)

x = 19
print_data(x)
print('----')

ptr = to_ptr(x)
ptr <<= 21

print_data(x)
```

This should give something like the output:

```
reference count:  16
type address:     9483264
number of digits: 1
lowest digit:     19
----
reference count:  15
type address:     9483264
number of digits: 1
lowest digit:     21
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

pointers.py replicates zeroed memory by just moving a `PyObject` 0 to the memory when our `CallocPointer` is initialized:

```py
bytes_a = (ctypes.c_ubyte * 24) \
    .from_address(id(0))

ctypes.memmove(address, bytes_a, len(bytes_a))
```

## Bindings

### Basics

The C standard library bindings wrap around the [ctypes](https://docs.python.org/3/library/ctypes.html) module internally.

Essentially, heres the steps for how a binding is executed:

_Highest to lowest level_

1. Binding function called (such as `strlen(string: str) -> int`)
2. `_make_char_pointer` converts `str` arguments to `bytes`, since `ctypes.c_char_p` is assignable to `bytes` but not `str`
3. `_base` executes the raw `ctypes` function specified in `_cstd.py`
4. `_base` then takes the response and maps it accordingly (e.g. converting `int` to `VoidPointer`)

### Raw CTypes Mappings

Unfortunately, I had to manually write the `argtypes` and `restypes` for all of the raw mappings.

A raw mapping could look something like this:

```py
# <comment showing function signature>
dll.name.argtypes = (ctypes.c_some_type, ctypes.c_some_type)
dll.name.restype = ctypes.c_some_type
```

- `dll` is the `ctypes.CDLL` object containing the C standard library
- `argtypes` must always be `Tuple[ctypes._CData, ...]`
- `restype` must always be `ctypes._CData`

If you are unfamiliar with the `_CData` type, it's simply a `ctypes` type (`c_void_p`, `c_char_p`, `c_int`, etc).

#### Example

_Actual source code_

```py
# size_t strlen(const char* str)
dll.strlen.argtypes = (ctypes.c_char_p,)
dll.strlen.restype = ctypes.c_size_t
```

### Type Conversions

Most of the type conversions are handled by `ctypes`, which can be found [here](https://docs.python.org/3/library/ctypes.html#fundamental-data-types). However, some types are converted in the pointers.py bindings.

A diagram of these conversions could look like this:

| CTypes Type | C Type      | Pointers.py Type   |
| ----------- | ----------- | ------------------ |
| `c_char_p`  | `char*`     | str                |
| `c_void_p`  | `void*`     | `VoidPointer`      |
| `POINTER`   | `T*`        | `TypedCPointer[T]` |
| `Structure` | `struct A`  | `Struct`           |
| `POINTER`   | `struct A*` | `StructPointer[A]` |

### High Level Mappings

Most of the actual binding signatures were autogenerated with something like the following:

```py
def fn_name(
    string_param: str,
    void_pointer_param: VoidPointer,
    typed_pointer_param: TypedCPointer[int]
) -> StructPointer[SomeStructObjectThatGetsReturned]:
    return _base(_make_char_pointer(string_param), void_pointer_param, typed_pointer_param)
```

As you can see, `string_param` has to go through the `_make_char_pointer` function to convert it to bytes.

You might be wondering, "why not just call `str.encode()`?". Lets look at the source for `_make_char_pointer`:

```py
def _make_char_pointer(data: Union[str, bytes]) -> bytes:
    return data if isinstance(data, bytes) else data.encode()
```

It can take in `str` _or_ `bytes`, and will return a bytes object either way. This is in case you want to actually pass bytes to the function.

But now you might be wondering, "why is the type hint always `str` and not `Union[str, bytes]`".

This is because I literally forgot to do that when writing the autogeneration function. This will be fixed in a later version.

### The Bind Function

Every single binding calls the `_bind` function and I haven't actually said much about that yet.

`_bind` is where the magic happens. It calls the C function and then maps the return type.

Let's dive into the source code:

```py
def _base(fn: "ctypes._NamedFuncPointer", *args) -> Any:
    res = fn(*args)
    res_typ = type(res)

    if res_typ.__name__.startswith("LP_"):
        struct_type = STRUCT_MAP.get(getattr(_cstd, res_typ.__name__[3:]))
        struct = (
            struct_type.from_existing(res.contents) if struct_type else None
        )  # fmt: off

        res = (
            TypedCPointer(ctypes.addressof(res), res_typ, ctypes.sizeof(res))
            if not issubclass(type(res.contents), ctypes.Structure)
            else StructPointer(id(struct), type(_not_null(struct)))
        )
    # type safety gets mad if i dont use elif here
    elif fn.restype is ctypes.c_void_p:
        res = VoidPointer(res, ctypes.sizeof(res))

    elif issubclass(res_typ, ctypes.Structure):
        struct = STRUCT_MAP.get(res_typ)
        if struct:
            res = struct.from_existing(res)

    return res
```

This looks pretty messy at first, and thats because it is.

The very first thing we do is call `fn`, which has type `_NamedFuncPointer`. This is simply the C function that we pass from the binding.

Then, we get the type of the response. But then we get to this line:

```py
if res_typ.__name__.startswith("LP_"):
```

To understand this, we need to go over something I hate about `ctypes`. We don't actually know what type we might get back.

The function can return a converted C type, a `ctypes.POINTER`, a `ctypes.Structure` object, or some other type that I don't know about.

This causes several problems:

- If we get an `int`, we don't know if it was mapped from `c_void_p`, `c_int`, `c_size_t`, or some other integer type.
- Returned `ctypes.Structure` objects have no type information, so we don't know what they contain.
- When we receive a `ctypes.POINTER`, a new type is created and is prefixed with `LP_`.

To solve the first problem, pointers.py has to set `restype` on every raw binding, and then we check if restype is supposed to be a pointer, in which case we return a `VoidPointer` object.

The next problem is solved with the `Struct` class. I manually got the signatures for structs in the C standard library and wrote a `Struct` object for them. Then, in `_cstd.py` we have the following object:

```py
STRUCT_MAP: Dict[Type[ctypes.Structure], Type[Struct]] = {
    tm: Tm,
    div_t: DivT,
    ldiv_t: LDivT,
    lconv: Lconv,
}
```

This object maps raw `ctypes` structures to their pointers.py equivalents.

Then, we can check in `_bind` if the `restype` was supposed to be a struct, and then we can map it accordingly.

The final problem brings us back to this line:

```py
if res_typ.__name__.startswith("LP_"):
```

Since a new object is created when a `ctypes.POINTER` object is returned, we can't use `isinstance` to check its type.

However, we can check to see if the type name begins with `LP_`, which will only be `True` if a `ctypes.POINTER` was returned.

We can then either build a `Struct` followed by a `StructPointer`, or just a `TypedCPointer`, and return it.

### Pointers

`TypedCPointer` and `VoidPointer` both inherit from the `_BaseCPointer` class.

This means that they have most of the same functionality, with two main differences:

- The way they dereference.
- How they work as `ctypes` parameters.

#### Void Pointers

Let's start with void pointers.

Void pointers dereference using the following code:

```py
def dereference(self) -> Optional[int]:
    """Dereference the pointer."""
    deref = ctypes.c_void_p.from_address(self.address)
    return deref.value
```

The `c_void_p` object is taken from the address, and then the value is returned.

I'm not entirely sure why, but `deref.value` can sometimes be `None` if the value was junk.

**Why is it an integer?** Not all types can be bound to Python correctly, so types such as `c_void_p` are integers with the address of said type instead of the object.

Pointers.py uses the same logic when using `VoidPointer` objects as parameters, and simply returns the address of the target object:

```py
# this is put inside a property to avoid overriding __init__
@property
def _as_parameter_(self) -> int:
    return self.address
```

#### Typed Pointers

Let's look at the source for dereferencing with `TypedCPointer`:

```py
def dereference(self) -> Optional[T]:
    """Dereference the pointer."""
    ctype = self.get_mapped(self.type)
    deref = ctype.from_address(self.address)
    return deref.value  # type: ignore
```

Since `TypedCPointer` takes a Python type and not a C type, we can't get it directly.

Instead, we have to use the `_BaseCPointer.get_mapped` utility to get the C type corresponding to our Python type (such as `int` to `c_int`).

Once we have the C type, all we have to do is it at the address, which again can be `None` if a junk value is used.

Now, handling `TypedCPointer` can be a bit trickier:

```py
@property
def _as_parameter_(self):
    ctype = self.get_mapped(self.type)
    deref = ctype.from_address(self.address)
    return ctypes.pointer(deref)
```

Since `ctypes` expects use to have an actual `ctypes.POINTER` object, we can't just use the address.

We have to use the same method above to get the mapped C type, and then we get the one at the address.

Finally, we convert it to a pointer and return it.

#### Struct Pointers

Struct pointers are extremely simple. They don't even inherit from `_BaseCPointer`.

This is because we don't even point to a C type. We just point to the `Struct` object, which itself holds the actual `ctypes.Structure`.

**Why do we need a new class, can't we just use `Pointer`?** Let's go ahead and look at `StructPointer`'s source:

```py
class StructPointer(Pointer[A]):
    """Class representing a pointer to a struct."""

    def __init__(self, address: int, data_type: Type[A]):
        super().__init__(address, data_type, True)

    @property
    def _as_parameter_(self):
        return self._address
```

We need `_as_parameter_` to allow it to be used in a `ctypes` call. Since we won't always have a binding for a struct, we can just use the address, like in `VoidPointer`.

The `increment_ref` is also passed to stop the struct from being garbage collected.
