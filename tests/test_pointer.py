from ward import test

from pointers import Pointer
from pointers import _ as m
from pointers import to_ptr


@test("creating pointers")
def _():
    assert type(to_ptr("a")) is Pointer
    assert type(m & "a") is Pointer
