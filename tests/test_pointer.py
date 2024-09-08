import sys

import pytest

from pointers import (BufferOverflowError, CompatibilityError, Pointer,
                      PyObjectPointer, to_ptr)


def test_pointer_type():
    ptr = to_ptr("hello")
    assert isinstance(ptr, Pointer)
    assert isinstance(ptr, PyObjectPointer)


def test_pointer_deref():
    x = "test"
    ptr = to_ptr(x)
    assert ptr.address == id(x)
    assert (~ptr) == x


def test_pointer_tracked_type():
    class Tracked:
        pass

    ptr = to_ptr(Tracked())
    assert isinstance(~ptr, Tracked)


def test_pointer_refcount():
    class Tracked:
        pass

    x = Tracked()
    ptr = to_ptr(x)
    assert ptr.refcount == sys.getrefcount(~ptr)
    assert ptr.refcount == sys.getrefcount(x)

    before = sys.getrefcount(x)
    ptr.refcount += 1
    assert (before + 1) == ptr.refcount
    ptr.refcount -= 1
    assert before == ptr.refcount


def test_size():
    class Tracked:
        pass

    x = "hello world"
    assert to_ptr(x).size() == sys.getsizeof(x)

    # This check is an implementation detail.
    # If this doesn't work in the future, feel free to remove it.
    assert to_ptr(Tracked()).size() == sys.getsizeof(Tracked())


def test_move_object():
    x = "do not touch this string ever again"
    to_ptr(x).move(to_ptr("hello world"))
    assert x == "hello world"

    with pytest.raises(BufferOverflowError):
        to_ptr("1").move(to_ptr("no good!"))


def test_object_deallocation():
    called = False

    class Tracked:
        def __del__(self):
            nonlocal called
            called = True

    # Sanity check
    Tracked()
    assert called is True

    called = False
    to_ptr(Tracked())
    assert called is True


def test_immortal_objects():
    called = False

    class Tracked:
        def __del__(self):
            nonlocal called
            called = True

    if sys.version_info < (3, 12):
        with pytest.raises(CompatibilityError):
            to_ptr(Tracked()).immortalize()
    else:
        to_ptr(Tracked()).immortalize()

    assert called is False
