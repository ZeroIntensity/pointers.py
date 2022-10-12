# CPython ABI Bindings

There is currently limited support for most of the CPython ABI.

The ABI follows the naming convention of `Py<namespace>_<method>`, so you may use one by importing the namespace from pointers.py:

```py
# example for PyEval_* methods
from pointers import PyEval

PyEval.something(...)
```

However, the method names are in `PascalCase`, and according to [PEP 8](https://peps.python.org/pep-0008/), Python functions should be named in `snake_case`.

Since pointers.py is PEP 8 compliant, method names have been converted to snake case.

Here's an example with `PyEval_GetFrame`:

```py
from pointers import PyEval

frame = PyEval.get_frame()  # calls the c PyEval_GetFrame function
```

## Casting Pointers

Some functions don't just return `PyObject`, and instead return something that can be casted instead (in this case, `PyFrameObject`):

Any binding that doesn't return a `PyObject*` is simply converted to a `StructPointer`:

```py
from pointers import PyEval

frame = PyEval.get_frame()
# frame is not a frame object, instead its StructPointer[FrameObject]
```

You may cast this pointer to the correct Python object by calling `struct_cast`:

```py
from pointers import PyEval, struct_cast

frame = struct_cast(PyEval.get_frame())
# frame is now a valid frame object!
```

## Limited Support

CPython ABI bindings are still unfinished, and any method that contains one of the following remains unsupported:

-   Uses a format string
-   Undocumented on [python.org](https://python.org)
-   Isn't documented properly
