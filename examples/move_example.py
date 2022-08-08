from pointers import Pointer, decay

a: str = "123"
b: str = "abc"


@decay
def move(ptr_a: Pointer[str], ptr_b: Pointer[str]):
    ptr_a <<= ptr_b


move(a, b)
print(a, b)  # abc abc
