from ward import raises, test

from pointers import (
    InvalidBindingParameter, Struct, StructPointer, TypedCPointer, VoidPointer
)
from pointers import _cstd as std
from pointers import (
    binds, c_free, c_malloc, cast, div, isspace, signal, sprintf, strcpy,
    strlen, to_c_ptr, to_struct_ptr, to_voidp, toupper
)
from pointers.std_structs import DivT


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

    signal(2, sighandler)

    with raises(InvalidBindingParameter):
        signal(2, bad)  # type: ignore

    signal(2, lambda x: ...)


@test("structs")
def _():
    res = div(10, 1)
    assert type(res) is DivT
    assert res.quot == 10

    class A(Struct):
        one: int
        two: int

    a = A(1, 2)

    class MyStruct(Struct):
        a: str
        b: str
        c: StructPointer[A]
        d: TypedCPointer[int]
        e: VoidPointer

    s = MyStruct(
        "a",
        "b",
        to_struct_ptr(a),
        to_c_ptr(1),
        to_voidp(
            to_c_ptr("hello"),
        ),
    )

    assert s.a == "a"
    assert type(s.c) is StructPointer
    assert type(s.d) is TypedCPointer
    assert type(s.e) is VoidPointer

    assert (~s.c) is a
    assert (~s.c).one == a.one
    assert ~s.d == 1
    assert ~cast(s.e, str) == "hello"

    class Foo(Struct):
        bar: TypedCPointer

    with raises(TypeError):
        Foo()


@test("custom bindings")
def _():
    @binds(std.dll.strlen)
    def strlen(a: str):
        ...

    strlen("test")

    with raises(InvalidBindingParameter):
        strlen(1)  # type: ignore


@test("chars")
def _():
    assert toupper(97) == "A"
    assert toupper("a") == "A"

    with raises(InvalidBindingParameter):
        isspace("hi")

    with raises(InvalidBindingParameter):
        isspace("")

    assert isspace(" ") != 0


@test("c pointers")
def _():
    ptr = to_c_ptr(1)
    ptr2 = to_c_ptr("hi")

    assert ~ptr == 1
    assert ~ptr2 == "hi"

    double_ptr = to_c_ptr(to_c_ptr(1))
    assert type(~double_ptr) is TypedCPointer
    assert ~(~double_ptr) == 1
    voidp = to_voidp(to_c_ptr(1))
    assert type(voidp) is VoidPointer

    assert ~cast(voidp, int) == 1
