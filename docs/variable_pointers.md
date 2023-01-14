# Variable Pointers

## What's the difference?

An object pointer (created by `to_ptr` or `Pointer.make_from`) points to the actual Python object (`PyObject*`), while a variable pointer points to that actual variable.

```py
hello = "123"
ptr = to_ptr(hello)
# ptr now points to "123", not "hello"
```

## Creation

You can make a variable pointer through `to_var_ptr`:

```py
from pointers import to_var_ptr

a = "hi"
ptr = to_var_ptr(a)
```

Note that of course you can't use a literal, because that isn't a variable:

```py
from pointers import to_var_ptr

ptr = to_var_ptr(123)  # ValueError
```

## Movement

Moving is much different when it comes to variable pointers. With an object pointer, you are overwriting that actual value, while with variable pointers you are just changing the value of that variable.

You can use movement the same way you would with an object pointer:

```py
from pointers import to_var_ptr

my_var = 1
my_ptr = to_var_ptr(my_var)
my_ptr <<= 2
print(my_var, 1)
# outputs 2 1, since we didnt overwrite 1 like we would with object pointers
```

You are free to use movement however you like with variable pointers. It isn't dangerous, unlike its counterpart.

### For C/C++ developers

Movement in variable pointers is equivalent to the following C code:

```c
int my_var = 1; // "my_var = 1"
int my_ptr = &my_var; // "my_ptr = to_var_ptr(my_var)"
*my_ptr = 2; // "my_ptr <<= 2"
// my_var is now 2 (the actual 1 is unchanged, thankfully)
```

## Assignment

Assignment works the same way as it does with object pointers:

```py
from pointers import to_var_ptr, NULL

hello = "world"
foo = "bar"

ptr = to_var_ptr(hello)
print(*ptr)  # world
ptr >>= NULL
# ...
ptr >>= foo
print(*ptr)  # bar
```
