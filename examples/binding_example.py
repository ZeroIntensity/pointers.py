from pointers import fclose, fopen, fprintf

file = fopen("/dev/null", "w")
fprintf(file, "hello world")
fclose(file)
