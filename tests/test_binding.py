from pointers import (
    to_c_ptr,
    TypedCPointer,
    StructPointer,
    localeconv,
    frexp,
    div,
    strlen,
)
from pointers._cstd import DivT


def test_to_c_ptr():
    ptr = to_c_ptr(5)
    assert type(ptr) is TypedCPointer
    assert ~ptr == 5
    ptr <<= 10
    assert ~ptr == 10


def test_bindings():
    assert type(localeconv()) is StructPointer
    assert frexp(8.0, to_c_ptr(10)) == 0.5
    div_t = div(10, 1)
    assert type(div_t) is DivT
    assert div_t.quot is 10

    r = strlen("test")
    assert type(r) is int
    assert r is 4
