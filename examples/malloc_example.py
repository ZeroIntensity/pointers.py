from pointers import malloc, free

memory = malloc(52)
memory <<= "abc"
print(*memory)  # abc
free(memory)
print(*memory)  # FreedMemoryError
