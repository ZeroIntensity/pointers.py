from pointers import Struct, to_struct_ptr


def test_struct():
    class MyStruct(Struct):
        a: str
        b: int

    instance = MyStruct("a", 1)
    assert instance.a == "a"
    assert instance._struct.b == 1
    instance.a = "test"
    assert instance.a == "test"
    assert instance._struct.a == "test"


def test_struct_ptr():
    class MyStruct(Struct):
        a: str
        b: int

    ptr = to_struct_ptr(MyStruct("a", 1))
    assert (~ptr).a == "a"
