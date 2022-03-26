from pointers import calloc_safe, calloc, NotEnoughChunks, free
import pytest


def test_calloc():
    mem = calloc(4, 28)
    mem <<= 1
    assert ~mem is 1
    free(mem)

    with pytest.raises(MemoryError):
        print(~mem)


def test_calloc_safe():
    memory = calloc_safe(4, 28)

    for index, ptr in enumerate(memory):
        ptr <<= index + 1

    array = [~i for i in memory]
    assert array == [1, 2, 3, 4]
    free(memory)


def test_calloc_validators():
    mem = calloc(1, 1)
    with pytest.raises(NotEnoughChunks):
        mem += 2

    with pytest.raises(IndexError):
        mem -= 1
