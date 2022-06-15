from pointers import Struct


class MyStruct(Struct):
    a: str
    b: str


a = MyStruct()
a.a = "a"
a.b = "b"

print(a, a.a, a.b)
