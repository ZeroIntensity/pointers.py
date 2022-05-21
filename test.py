from src.pointers import to_ptr

class test:
    pass

instance = test()
ptr = to_ptr(instance)

print(~ptr)