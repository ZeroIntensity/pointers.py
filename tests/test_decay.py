from pointers import decay, Pointer, FrozenPointer
import pytest

def test_decay():
    @decay
    def x(a: Pointer[str]):
        return type(a)

    assert x("a") is Pointer

def test_decay_again():
    @decay
    def x(a: FrozenPointer[str], b: Pointer[str], c: str):
        assert type(a) is FrozenPointer
        assert type(b) is Pointer
        assert type(c) is str
    
    x("a", "b", "c")