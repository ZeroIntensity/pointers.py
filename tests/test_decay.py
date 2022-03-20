from pointers import decay, Pointer


def test_decay():
    @decay
    def x(a: Pointer[str]):
        return type(a)

    assert x("a") is Pointer
