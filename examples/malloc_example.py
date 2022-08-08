from pointers import free, malloc

memory = malloc(52)
memory <<= "abc"
print(*memory)  # abc
free(memory)
print(*memory)  # FreedMemoryError
