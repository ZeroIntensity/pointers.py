from ward import raises, test

from pointers import InvalidSizeError, Pointer
from pointers import _ as m
from pointers import strlen, to_c_ptr, to_ptr
from pointers.exceptions import NullPointerError


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


@test("null pointers")
def _():
    ptr = to_ptr(0)
    ptr >>= None

    with raises(NullPointerError):
        print(~ptr)

    with raises(NullPointerError):
        print(*ptr)


@test("operator magic")
def _():
    ptr = m & "test"
    assert type(ptr) is Pointer
    assert m * ptr == "test"


@test("c pointers")
def _():
    a = to_c_ptr("test")
    assert ~a == "test"
    c = to_c_ptr(1)
    assert ~c == 1
    assert strlen(b"test") == 4
