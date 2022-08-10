from ward import raises, test

from pointers import InvalidSizeError, Pointer
from pointers import _ as m
from pointers import to_c_ptr, to_ptr


@test("creating pointers")
def _():
    assert type(to_ptr("a")) is Pointer
    assert type(m & "a") is Pointer


@test("dereferencing")
def _():
    ptr = to_ptr("test")
    assert ~ptr == "test"
    cptr = to_c_ptr("test")
    assert ~cptr == "test"


@test("assignment")
def _():
    ptr = to_ptr("test")
    ptr.assign("a")

    assert ~ptr == "a"
    ptr >>= "test"
    assert ~ptr == "test"


@test("movement")
def _():
    a = "teststring"
    ptr = to_ptr(a)
    ptr <<= "hi"

    assert a == "hi"

    with raises(InvalidSizeError):
        ptr <<= "hello world"
