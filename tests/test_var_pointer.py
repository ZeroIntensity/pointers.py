from ward import raises, test

from pointers import NULL, NullPointerError, VarPointer, to_var_ptr

"""
@test("creating variable pointers")
def _():
    var = "hello"
    ptr = to_var_ptr(var)

    assert type(ptr) is VarPointer
    assert ~ptr == var

    with raises(TypeError):
        to_var_ptr("hello")

@test("variable pointer movement")
def _():
    var = "hello"
    var2 = "123456"
    ptr = to_var_ptr(var)
    ptr2 = to_var_ptr(var2)

    ptr <<= "hi"
    print(var, ~ptr)
    assert var == "hi"

    ptr <<= ptr2
    assert var == var2

@test("variable pointer assignment")
def _():
    var = "hello"
    var2 = "123456"
    ptr = to_var_ptr(var)

    ptr >>= var2
    assert ~ptr == var2
    ptr >>= NULL

    with raises(NullPointerError):
        assert ~ptr

@test("variable pointer dereferencing")
def _():
    var = "hello"
    var2 = "1234"
    ptr = to_var_ptr(var)

    assert ~ptr == var
    assert ptr.address == id(var)
    ptr >>= var2
    assert ~ptr == var2
"""
