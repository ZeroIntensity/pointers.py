from pointers import Reference, ref

my_value = ref(0)

def test(my_ref: Reference[int]) -> None:
    print(f"now borrowing {my_ref}")
    my_ref.own()

test(my_value)
