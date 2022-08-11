import sys

from ward import raises, test

from pointers import InvalidBindingParameter
from pointers import _cstd as std
from pointers import (
    binds, c_free, c_malloc, cast, div, signal, sprintf, strcpy, strlen
)
from pointers._cstd import DivT


@test("c strings")
def _():
    ptr = c_malloc(2)
    strcpy(ptr, "a")
    assert ~cast(ptr, bytes) == b"a"
    c_free(ptr)


@test("format strings")
def _():
    ptr = c_malloc(2)
    sprintf(ptr, "%s", "a")
    assert ~cast(ptr, bytes) == b"a"
    c_free(ptr)


@test("argument validation")
def _():
    with raises(InvalidBindingParameter):
        strlen(1)  # type: ignore

    assert strlen("test") == 4


@test("functions")
def _():
    def sighandler(signum: int):
        ...

    def bad(signum: str):
        ...

    signal(13, sighandler)

    with raises(InvalidBindingParameter):
        signal(13, bad)  # type: ignore

    signal(2, lambda x: ...)


@test("structs")
def _():
    res = div(10, 1)
    assert type(res) is DivT
    assert res.quot == 10


@test("custom bindings")
def _():
    @binds(std.dll.strlen)
    def strlen(a: str):
        ...

    strlen("test")

    with raises(InvalidBindingParameter):
        strlen(1)  # type: ignore
