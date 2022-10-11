import ctypes

from _pointers import add_ref
from pointers import NULL, InvalidSizeError, Pointer, SegmentViolation
from pointers import _ as m
from pointers import handle, to_c_ptr, to_ptr
from pointers.exceptions import NullPointerError
from ward import raises, test


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


@test("movement")
def _():
    a = 763723
    ptr = to_ptr(a)
    ptr <<= 2

    assert a == 2

    with raises(InvalidSizeError):
        ptr <<= 758347580937450893


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

    ptr2: Pointer[int] = to_ptr(NULL)
    ptr2 >>= 1

    ptr2 >>= NULL


@test("operator magic")
def _():
    ptr = m & "test"
    assert type(ptr) is Pointer
    assert m * ptr == "test"
