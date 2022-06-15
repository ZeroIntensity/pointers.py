from pointers import fopen, fprintf, fclose

file = fopen("/dev/null", "w")
fprintf(file, "hello world")
fclose(file)
