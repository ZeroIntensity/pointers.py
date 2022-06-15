from pointers import (
    to_ptr,
    Pointer,
    FrozenPointer,
    to_const_ptr,
    IsFrozenError,
)
import pytest


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
    num: int = 432154
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


def test_tracked():
    ptr = to_ptr(SomeObj())
    assert ptr.tracked


# we cant test things like DereferenceError here because of the garbage collector being weird
