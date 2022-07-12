from pointers import (
    to_ptr,
    Pointer,
    FrozenPointer,
    to_const_ptr,
    IsFrozenError,
)
import pytest
from sys import getrefcount


class SomeObj:
    pass


def test_to_ptr():
    assert type(to_ptr("a")) is Pointer


def test_assign():
    a = to_ptr("a")
    b = to_ptr("b")

    a >>= b
    assert b.address == a.address


def test_move():
    num: int = 4321545
    target: int = 7676745
    # ^^ some random numbers

    a = to_ptr(target)
    b = to_ptr(num)

    a <<= b
    assert num == target


def test_frozen():
    ptr = to_const_ptr("a")

    assert type(ptr) is FrozenPointer

    with pytest.raises(IsFrozenError):
        ptr >>= "abc"


def test_ref_counts():
    ptr = to_ptr(SomeObj())
    assert type(~ptr) is SomeObj
    assert getrefcount(~ptr) == 3

def test_set_attr():
    ptr = to_ptr(str)
    ptr.set_attr("a", "b")

    ptr2 = to_ptr("test")
    ptr2.set_attr("b", "c")
    assert str.a == "b"
    assert str.b == "c"
