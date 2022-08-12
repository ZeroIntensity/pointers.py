from typing_extensions import Annotated
from ward import test

from pointers import Pointer, decay, decay_annotated, decay_wrapped


@test("decay")
def _():
    @decay
    def func(a: str, b: int, c: Pointer):
        assert type(a) is str
        assert type(b) is int
        assert type(c) is Pointer

    func("a", 1, "c")

    @decay
    def func2(a: str, b: int, c: Pointer[str]):
        assert type(a) is str
        assert type(b) is int
        assert type(c) is Pointer

    func2("a", 1, "c")


@test("decay with annotated")
def _():
    @decay_annotated
    def func(a: str, b: int, c: Annotated[str, Pointer]):
        assert type(a) is str
        assert type(b) is int
        assert type(c) is Pointer

    func("a", 1, "c")

    @decay_annotated
    def func2(a: str, b: int, c: Annotated[str, Pointer[str]]):
        assert type(a) is str
        assert type(b) is int
        assert type(c) is Pointer

    func2("a", 1, "c")


@test("decay with wrapped")
def _():
    def wrapper(a: str, b: int, c: str) -> None:
        ...

    @decay_wrapped(wrapper)
    def func(a: str, b: int, c: Pointer):
        assert type(a) is str
        assert type(b) is int
        assert type(c) is Pointer

    func("a", 1, "c")

    @decay_wrapped(wrapper)
    def func2(a: str, b: int, c: Pointer[str]):
        assert type(a) is str
        assert type(b) is int
        assert type(c) is Pointer

    func2("a", 1, "c")
