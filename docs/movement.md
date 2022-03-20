# Movement

## Overwriting memory

To overwrite a value in memory, use `Pointer.move`.

```py
from pointers import to_ptr

a = "test"
b = "hello world"

ptr = to_ptr(a)
ptr2 = to_ptr(b)

ptr.move(ptr2) # overwrites a with "hello world"
print(~ptr)
```

This is extremely dangerous, since we are overwriting the string `"test"` with `"hello world"`.

That means that if we try to use the string `"test"` anywhere else, then it will be switched with `"hello world"`

```py
ptr.move(ptr2)
print(~ptr)
print("test") # prints "hello world"
```

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

## Consequences

After you are finishing crying after accidentally overwriting your newborn child using this library, what actually happens when we break something with overwriting?

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

### Other Issues

You are less likely to run into problems with other methods, but it is definetly possible:

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

Once again, this is not a Python error that you can try/except.

Whats happening here is that we are trying to access memory at address `1`, which doesn't exist.

The operating system understands this, and then terminates the program using `SIGSEGV`, otherwise known as a segmentation fault.
