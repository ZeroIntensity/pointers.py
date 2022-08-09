# Movement

## Overwriting memory

To overwrite a value in memory, use `Pointer.move`.

```py
from pointers import to_ptr

a = "test"
b = "abcd"

ptr = to_ptr(a)
ptr2 = to_ptr(b)

ptr.move(ptr2) # overwrites a with "abcd"
print(~ptr)
```

This is extremely dangerous, since we are overwriting the string `"test"` with `"abcd"`.

That means that if we try to use the string `"test"` anywhere else, then it will be switched with `"abcd"`

**Note:** Data movement will only change the literal on cached types (such as `int` and `str`)

```py
ptr.move(ptr2)
print(~ptr)
print("test") # prints "abcd"
```

## Buffer Overflows

By default, pointers.py doesn't allow you to

```py
a = to_ptr("test")
b = to_ptr("abcdefg")

a.move(b) # InvalidSizeError
```

This can be bypassed by passing `unsafe=True` to `move`:

```py
a = to_ptr("test")
b = to_ptr("abcdefg")

a.move(b, unsafe=True) # works just fine
```

**This is extremely dangerous and makes your code vulnerable to buffer overflow attacks.**

### For C/C++ developers

Data movement is equivalent to just assigning values to a dereferenced pointers. Example:

```cpp
int main() {
    int a = 0; // using int instead of string
    int* ptr = &a;

    *ptr = 1; // unfortunately in python, this would overwrite 0 and not a
}
```

### Operator

Like all other pointer operations, pointers.py has an operator for move:

```py
ptr <<= ptr2 # same as above
print(~ptr)
print("test")
```

Remember, `>>` is pointer assignment, and `<<` is data movement.

Like assignment with `>>`, you don't need to pass a pointer:

```py
from pointers import to_ptr

a = "test"

ptr = to_ptr(a)
ptr <<= "hello world" # works just fine
print(~ptr)
```

If you would like to run an unsafe move, you can use the `^` operator, which will pass it for you:

```py
ptr = to_ptr(a)
ptr ^= "hello world" # same as ptr.move(to_ptr("hello world"), unsafe=True)
print(~ptr)
```

## Consequences

What actually happens when we break something with overwriting?

Lets use the following code as an example:

```py
from pointers import to_ptr

a = 1
b = 2

ptr = to_ptr(a)
ptr2 = to_ptr(b)

ptr <<= ptr2
print(1, 2) # prints "2 2"
```

This will work, but then you should get something like this:

```
free(): invalid pointer
Fatal Python error: Aborted

Current thread 0x00007f5a2fa2d740 (most recent call first):
<no Python frame>
```

This is **not** a Python exception, it's how Python is handling `SIGABRT`. **You cannot try/except this error.**

It's an internal Python error, and it's occuring because we overwrote `1` with `2` (so `1 == 2` would evalute to `True`!)

### Other dangers of overwriting

If your code runs successfully, and you are updating a non-cached type, then everything should be ok, right? Unfortunately, this is not the case.

Lets use the code below as an example:

```py
from pointers import to_ptr

class a:
    def __init__(self, a: str) -> None:
        self.a = a

instance = a("a")
second_instance = a("b")
ptr = to_ptr(instance)

ptr <<= second_instance
print(ptr.a) # b
```

This will execute just fine, and since `a` isn't a cached type, then it isn't changed for the entire interpreter.

Now lets look at the code pointers.py uses for data movement:

```py
bytes_a = (ctypes.c_ubyte * sys.getsizeof(~data)) \
    .from_address(data.address)
bytes_b = (ctypes.c_ubyte * sys.getsizeof(~self)) \
    .from_address(self.address)

ctypes.memmove(bytes_b, bytes_a, len(bytes_a))
```

Both pointers get turned into a byte stream, and then we use C to change the original stream.

**Why is this an issue?**
Python objects have internal data like reference counts, type, length that will be corrupted by blindly copying over them.
