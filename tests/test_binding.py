from pointers import (
    to_c_ptr,
    StructPointer,
    localeconv,
    div,
    strlen,
    c_malloc,
    c_free,
    sprintf,
    cast
)
from pointers._cstd import DivT

# pytest breaks c pointers for whatever reason

def test_bindings():
    assert type(localeconv()) is StructPointer
    div_t = div(10, 1)
    assert type(div_t) is DivT
    assert div_t.quot is 10

    r = strlen("test")
    assert r == 4
    assert type(r) is int

def test_to_c_ptr():
    a = to_c_ptr('test')
    assert a.type is str
    assert ~a == 'test'

def test_strings():
    mem = c_malloc(2)
    sprintf(mem, "%s", "a")  # testing format strings
    ptr = cast(mem, bytes)
    assert ~ptr == b"a"
    c_free(mem)