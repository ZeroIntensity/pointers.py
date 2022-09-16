from ward import raises, test

from pointers import NULL, InvalidSizeError, Pointer
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
    assert m * ptr == "test"
    assert (*ptr,) == (~ptr,)
    cptr = to_c_ptr("test")
    assert ~cptr == "test"


@test("assignment")
def _():
    ptr = to_ptr("test")
    ptr.assign("a")

    assert ~ptr == "a"
    ptr >>= "test"
    assert ~ptr == "test"

    with raises(TypeError):
        ptr >>= 1  # type: ignore


@test("movement")
def _():
    a = "teststring"
    ptr = to_ptr(a)
    ptr <<= "hi"

    assert a == "hi"

    with raises(InvalidSizeError):
        ptr <<= "hello world"

    with raises(TypeError):
        ptr <<= 1  # type: ignore


@test("assignment with tracked types")
def _():
    class A:
        def __init__(self, value: str) -> None:
            self.value = value

    obj = A("hello")
    ptr = to_ptr(A("world"))
    assert (~ptr).value == "world"

    ptr >>= obj
    assert (~ptr).value == "hello"
    ptr2 = to_ptr(obj)
    ptr2 >>= A("12345")
    assert (~ptr2).value == "12345"


@test("null pointers")
def _():
    ptr = to_ptr(0)
    ptr >>= NULL

    with raises(NullPointerError):
        print(~ptr)

    with raises(NullPointerError):
        print(*ptr)

    with raises(NullPointerError):
        print(~to_ptr(NULL))


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
