from pointers import malloc, free, MallocPointer, IsMallocPointerError
import pytest

def test_malloc_pointer():
    mem = malloc(1)
    assert type(mem) is MallocPointer

    with pytest.raises(IsMallocPointerError):
        mem.type

    with pytest.raises(IsMallocPointerError):
        mem >>= "abc"

def test_malloc():
    mem = malloc(52)
    mem <<= "abc"
    assert ~mem == "abc"

def test_free():
    mem = malloc(52)
    mem <<= "abc"
    free(mem)

    with pytest.raises(MemoryError):
        print(~mem)