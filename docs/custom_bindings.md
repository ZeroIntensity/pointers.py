# Custom Bindings

If you are using `ctypes` and would like a nicer API for yourself or your users, pointers.py makes it easy to create custom bindings.

For this example we are going to use the C standard library, but you can use whatever DLL you want.

```py
import ctypes

dll = ctypes.CDLL("libc.so.6")
```

Setting `argtypes` and `restype` aren't required, but are recommended to help pointers.py convert arguments and ensure the right parameters are passed to your C functions:

```py
import ctypes

dll = ctypes.CDLL("libc.so.6")

dll.strlen.restype = ctypes.c_int
dll.strlen.argtypes = (ctypes.c_char_p,)
```

Now, we can use the `binds` decorator to create our binding:

```py
import ctypes
from pointers import binds

dll = ctypes.CDLL("libc.so.6")

dll.strlen.restype = ctypes.c_int
dll.strlen.argtypes = (ctypes.c_char_p,)

@binds(dll.strlen)
def strlen(string: str) -> int:
    ... # you don't need to define any function body at all

print(strlen('test')) # 4
```

If you don't care about type safety, then you can use the `binding` function instead:

```py
import ctypes
from pointers import binding

dll = ctypes.CDLL("libc.so.6")

dll.strlen.restype = ctypes.c_int
dll.strlen.argtypes = (ctypes.c_char_p,)

strlen = binding(dll.strlen) # this isnt type safe!
print(strlen('test')) # 4
```

## Structs

When your function returns a struct, it gets a little bit more complicated.

Setting the `restype` is **required** when returning a struct, meaning we have to define a `ctypes.Structure` object:

```py
from pointers import binds, Struct
import ctypes

dll = ctypes.CDLL("libc.so.6")

class div_t(ctypes.Structure):
    _fields_ = [
        ("quot", ctypes.c_int),
        ("rem", ctypes.c_int),
    ]

dll.div.restype = div_t
```

Now, if you don't care about type safety you can just use the raw `ctypes.Structure` object that the binding will return.

Otherwise, we have to create a `Struct` object that corresponds to our original `ctypes.Structure`:

```py
class div_t(ctypes.Structure):
    _fields_ = [
        ("quot", ctypes.c_int),
        ("rem", ctypes.c_int),
    ]

class DivT(Struct):
    quot: int
    rem: int

dll.div.restype = div_t
```

Finally, just pass our `Struct` object into the `struct` argument of our binding:

```py
class div_t(ctypes.Structure):
    _fields_ = [
        ("quot", ctypes.c_int),
        ("rem", ctypes.c_int),
    ]

class DivT(Struct):
    quot: int
    rem: int

dll.div.restype = div_t

@binds(dll.div, struct=DivT) # this tells pointers.py that this struct will be returned
def div(numer: int, denom: int) -> DivT:
    ...
```

You can do the same with the `binding` function:

```py
div = binding(dll.div, struct=DivT)
```

## Struct Pointers

If your function returns a pointer to a struct, then handling it is super simple.

All you have to do is set the `restype` of your `ctypes` function to a pointer to a struct:

```py
from pointers import binds, Struct
import ctypes
from typing import Any

dll = ctypes.CDLL("libc.so.6")

class Lconv(Struct):
    decimal_point: str
    thousands_sep: str
    grouping: str
    int_curr_symbol: str
    currency_symbol: str
    mon_decimal_point: str
    mon_thousands_sep: str
    mon_grouping: str
    positive_sign: str
    negative_sign: str
    frac_digits: str
    p_cs_precedes: str
    p_sep_by_space: str
    n_sep_by_space: str
    p_sign_posn: str
    n_sign_posn: str

class lconv(ctypes.Structure):
    _fields_ = [
        ("decimal_point", ctypes.c_char_p),
        ("thousands_sep", ctypes.c_char_p),
        ("grouping", ctypes.c_char_p),
        ("int_curr_symbol", ctypes.c_char_p),
        ("currency_symbol", ctypes.c_char_p),
        ("mon_decimal_point", ctypes.c_char_p),
        ("mon_thousands_sep", ctypes.c_char_p),
        ("mon_grouping", ctypes.c_char_p),
        ("positive_sign", ctypes.c_char_p),
        ("negative_sign", ctypes.c_char_p),
        ("int_frac_digits", ctypes.c_char),
        ("frac_digits", ctypes.c_char),
        ("p_cs_precedes", ctypes.c_char),
        ("p_sep_by_space", ctypes.c_char),
        ("n_sep_by_space", ctypes.c_char),
        ("p_sign_posn", ctypes.c_char),
        ("n_sign_posn", ctypes.c_char),
    ]

dll.localeconv.restype = ctypes.POINTER(lconv)

@binds(dll.localeconv, struct=Lconv)
def localeconv() -> Any:
    ...
```

Once again, you need to create a `Struct` object that matches the `Structure` and pass it to the binding.

For type safety, you can hint the return type of your binding to be `StructPointer`:

```py
@binds(dll.localeconv, struct=Lconv)
def localeconv() -> StructPointer[Lconv]:
    ...
```
