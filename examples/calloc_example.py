from pointers import calloc, free

array = calloc(10, 28)

for index, ptr in enumerate(array):
    ptr <<= index + 1

py_array = [~i for i in array]
print(py_array)
free(array)
