import sys

from ward import raises, test

from pointers import FreedMemoryError, InvalidSizeError, calloc, free, malloc, realloc


@test("malloc and free")
def _():
    ptr = malloc(28)
    assert ptr.freed is False
    assert ptr.assigned is False
    ptr <<= 1
    assert ptr.assigned is True

    with raises(InvalidSizeError):
        ptr <<= "hello"

    free(ptr)

    with raises(FreedMemoryError):
        print(~ptr)

    with raises(FreedMemoryError):
        free(ptr)

    with raises(FreedMemoryError):
        ptr.ensure_valid()

    assert ptr.freed is True


@test("calloc with enumerations")
def _():
    ptr = calloc(4, 28)

    for index, value in enumerate(ptr):
        value <<= index + 1

    assert [~i for i in ptr] == [1, 2, 3, 4]

    free(ptr)

    with raises(FreedMemoryError):
        print(~ptr)


@test("calloc")
def _():
    ptr = calloc(4, 28)
    assert ptr.chunks == 4

    with raises(InvalidSizeError):
        ptr <<= "hello"

    for index, value in enumerate(ptr):
        value <<= index + 1

    with raises(IndexError):
        ptr -= 1

    with raises(IndexError):
        ptr += 10

    assert ~ptr == 1
    ptr += 1
    assert ptr.current_index == 1
    assert ~ptr == 2

    ptr[0] = 10
    assert ~ptr[0] == 10

    free(ptr)

    with raises(FreedMemoryError):
        ptr -= 1

    with raises(FreedMemoryError):
        ptr <<= "test"


@test("realloc")
def _():
    ptr = malloc(28)
    ptr <<= 1

    realloc(ptr, 30)
    assert ~ptr == 1
    target: str = "hello world"
    nptr = realloc(ptr, sys.getsizeof(target) + 1)
    assert nptr is ptr

    ptr <<= target
    assert ~ptr == target

    with raises(InvalidSizeError):
        realloc(ptr, 10)


@test("allocation with tracked types")
def _():
    class A:
        def __init__(self, value: str) -> None:
            self.value = value

    obj = A("hello")
    ptr = malloc(sys.getsizeof(obj))
    ptr <<= obj

    # assert (~ptr).value == "hello"
    # free(ptr)
    # assert obj.value == "hello"
