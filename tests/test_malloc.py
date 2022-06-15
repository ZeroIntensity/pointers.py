from pointers import (
    malloc,
    free,
    MallocPointer,
    IsMallocPointerError,
    realloc,
    FreedMemoryError,
    InvalidSizeError,
    DereferenceError,
)
import pytest


def test_malloc_pointer():
    mem = malloc(1)
    assert type(mem) is MallocPointer

    with pytest.raises(DereferenceError):
        mem.dereference()

    with pytest.raises(InvalidSizeError):
        mem <<= "abc"

    with pytest.raises(IsMallocPointerError):
        mem.type

    with pytest.raises(IsMallocPointerError):
        mem >>= "abc"

    free(mem)


def test_malloc():
    mem = malloc(52)
    mem <<= "abc"
    assert ~mem == "abc"
    free(mem)


def test_free():
    mem = malloc(52)
    mem <<= "abc"
    free(mem)

    with pytest.raises(FreedMemoryError):
        print(~mem)


def test_realloc():
    mem = malloc(52)
    mem <<= "abc"
    realloc(mem, 53)

    assert mem.size == 53

    with pytest.raises(InvalidSizeError):
        mem <<= "abcde"

    mem <<= "abcd"
    assert ~mem == "abcd"
    free(mem)
