import sys

from ward import raises, test

from pointers import (
    FreedMemoryError, InvalidSizeError, calloc, free, malloc, realloc
)


@test("malloc and free")
def _():
    ptr = malloc(28)
    ptr <<= 1

    with raises(InvalidSizeError):
        ptr <<= "hello"

    free(ptr)

    with raises(FreedMemoryError):
        print(~ptr)

    with raises(ValueError):
        free(ptr)


@test("calloc and free")
def _():
    ptr = calloc(4, 28)

    for index, value in enumerate(ptr):
        value <<= index + 1

    assert [~i for i in ptr] == [1, 2, 3, 4]

    free(ptr)

    with raises(FreedMemoryError):
        print(~ptr)


@test("realloc")
def _():
    ptr = malloc(28)
    ptr <<= 1

    realloc(ptr, 30)
    assert ~ptr == 1
    target: str = "hello world"
    realloc(ptr, sys.getsizeof(target) + 1)

    ptr <<= target
    assert ~ptr == target
