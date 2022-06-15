from pointers import calloc, NotEnoughChunks, free, FreedMemoryError
import pytest


def test_calloc():
    mem = calloc(4, 28)
    assert ~mem == 0
    mem <<= 1
    assert ~mem == 1
    free(mem)

    with pytest.raises(FreedMemoryError):
        print(~mem)

    memory = calloc(4, 28)

    for index, ptr in enumerate(memory):
        ptr <<= index + 1

    array = [~i for i in memory]
    assert array == [1, 2, 3, 4]


def test_calloc_validators():
    mem = calloc(1, 1)
    with pytest.raises(NotEnoughChunks):
        mem += 2

    with pytest.raises(IndexError):
        mem -= 1

    free(mem)
