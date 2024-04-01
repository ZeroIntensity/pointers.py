from pointers import Reference, MutReference, ref

my_value = ref(0)

def test(my_ref: MutReference[int]) -> None:
    print(f"now borrowing mutable {my_ref}")
    my_ref <<= 1

with my_value.mut():
    my_value <<= 2

test(my_value.mut())
print(~my_value)  # 1