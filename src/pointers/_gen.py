from ._cstd import dll
from ctypes import *

TYPE_MAP = {
    c_char_p: str,
    c_long: int,
    c_char: str,
    c_ulong: int,
    c_int: int,
    c_void_p: "CVoidPointer",
    c_double: int,
    None: None,
}

STR_TYPE_MAP = {
    "char*": "str",
    "int": "int",
    "void*": "CTypedPointer[Any]",
    "FILE*": "CVoidPointer",
    "double*": "CTypedPointer[float]",
    "char**": "CTypedPointer[str]",
    "int*": "CTypedPointer[int]",
    "double": "float",
    "fpos_t*": "CVoidPointer",
    "size_t": "int",
    "time_t": "int",
    "time_t*": "CTypedPointer[int]",
    "clock_t": "int",
}


def main(data: str):
    last: str = ""
    lastsig: str = ""

    for i in data.splitlines():
        if i.startswith("#"):
            lastsig = i

        if i.startswith("dll."):
            name = i.split(".")[1]
            if last != name:
                last = name
                fn = getattr(dll, name)
                typ = TYPE_MAP[fn.restype]
                tname = (
                    getattr(typ, "__name__", None) if not typ == "CVoidPointer" else typ
                )
                if not tname:
                    tname = "None"
                params_str = lastsig[lastsig.index("(") + 1 : lastsig.index(")")]
                params = []

                for param_sig in params_str.split(","):
                    if not param_sig == "void":
                        typ, pname = param_sig.split(" ")[-2:]
                        mapped = STR_TYPE_MAP.get(typ)
                        params.append(
                            (
                                "string"
                                if pname == "str"
                                else "fmt"
                                if pname == "format"
                                else "*args"
                                if pname == "..."
                                else pname,
                                mapped or typ if pname != "..." else "str",
                            )
                        )

                print(
                    f"""def {name}({', '.join([f'{pname}: {typ}' for pname, typ in params])}) -> {tname}:
    return _base(dll.{name}{', ' if params else ''}{', '.join([pname if not typ == 'str' else f'_make_char_pointer({pname})' if pname != '*args' else pname for pname, typ in params])})"""
                )


string = """# int isalnum(int c)
dll.isalnum.argtypes = (ctypes.c_int,)
dll.isalnum.restype = ctypes.c_int
# int isalpha(int c)
dll.isalpha.argtypes = (ctypes.c_int,)
dll.isalpha.restype = ctypes.c_int
# int iscntrl(int c)
dll.iscntrl.argtypes = (ctypes.c_int,)
dll.iscntrl.restype = ctypes.c_int
# int isdigit(int c)
dll.isdigit.argtypes = (ctypes.c_int,)
dll.isdigit.restype = ctypes.c_int
# int isgraph(int c)
dll.isgraph.argtypes = (ctypes.c_int,)
dll.isgraph.restype = ctypes.c_int
# int islower(int c)
dll.islower.argtypes = (ctypes.c_int,)
dll.islower.restype = ctypes.c_int
# int isprint(int c)
dll.isprint.argtypes = (ctypes.c_int,)
dll.isprint.restype = ctypes.c_int
# int ispunct(int c)
dll.ispunct.argtypes = (ctypes.c_int,)
dll.ispunct.restype = ctypes.c_int
# int isspace(int c)
dll.isspace.argtypes = (ctypes.c_int,)
dll.isspace.restype = ctypes.c_int
# int isupper(int c)
dll.isupper.argtypes = (ctypes.c_int,)
dll.isupper.restype = ctypes.c_int
# int isxdigit(int c)
dll.isxdigit.argtypes = (ctypes.c_int,)
dll.isxdigit.restype = ctypes.c_int
# int tolower(int c)
dll.tolower.argtypes = (ctypes.c_int,)
dll.tolower.restype = ctypes.c_int
# int toupper(int c)
dll.toupper.argtypes = (ctypes.c_int,)
dll.toupper.restype = ctypes.c_int
# char* setlocale(int category, const char* locale)
dll.setlocale.argtypes = (ctypes.c_int, ctypes.c_char_p)
dll.setlocale.restype = ctypes.c_char_p
# double frexp(double x, int* exponent)
dll.frexp.argtypes = (ctypes.c_double, ctypes.POINTER(ctypes.c_int))
dll.frexp.restype = ctypes.c_double
# double ldexp(double x, int exponent)
dll.ldexp.argtypes = (ctypes.c_double, ctypes.c_int)
dll.ldexp.restype = ctypes.c_double
# double modf(double x, double* integer)
dll.modf.argtypes = (ctypes.c_double, ctypes.POINTER(ctypes.c_double))
dll.modf.restype = ctypes.c_double
# void (*signal(int sig, void (*func)(int)))(int)
dll.signal.argtypes = (ctypes.c_int, ctypes.c_void_p)
dll.signal.restype = None
# int raise(int sig)
c_raise.argtypes = (ctypes.c_int,)
c_raise.restype = ctypes.c_int
# int fclose(FILE* stream)
dll.fclose.argtypes = (ctypes.c_void_p,)
dll.fclose.restype = ctypes.c_int
# void clearerr(FILE* stream)
dll.clearerr.argtypes = (ctypes.c_void_p,)
dll.clearerr.restype = None
# int feof(FILE* stream)
dll.feof.argtypes = (ctypes.c_void_p,)
dll.feof.restype = ctypes.c_int
# int ferror(FILE* stream)
dll.ferror.argtypes = (ctypes.c_void_p,)
dll.ferror.restype = ctypes.c_int
# int fflush(FILE* stream)
dll.fflush.argtypes = (ctypes.c_void_p,)
dll.fflush.restype = ctypes.c_int
# int fgetpos(FILE* stream, fpos_t* pos)
dll.fgetpos.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
dll.fgetpos.restype = ctypes.c_int
# FILE* fopen(const char* filename, const char* mode)
dll.fopen.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.fopen.restype = ctypes.c_void_p
# size_t fread(void* ptr, size_t size, size_t nmemb, FILE* stream)
dll.fread.argtypes = (ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t)
dll.fread.restype = ctypes.c_size_t
# FILE* freopen(const char* filename, const char* mode, FILE* stream)
dll.freopen.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p)
dll.freopen.restype = ctypes.c_void_p
# int fseek(FILE* stream, long int offset, int whence)
dll.fseek.argtypes = (ctypes.c_void_p, ctypes.c_long, ctypes.c_int)
dll.fseek.restype = ctypes.c_int
# int fsetpos(FILE* stream, const fpos_t* pos)
dll.fsetpos.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
dll.fsetpos.restype = ctypes.c_int
# long int ftell(FILE* stream)
dll.ftell.argtypes = (ctypes.c_void_p,)
dll.ftell.restype = ctypes.c_long
# size_t fwrite(const void* ptr, size_t size, size_t nmemb, FILE* stream)
dll.fwrite.argtypes = (
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_size_t,
    ctypes.c_void_p,
)
dll.fwrite.restype = ctypes.c_size_t
# int remove(const char* filename)
dll.remove.argtypes = (ctypes.c_char_p,)
dll.remove.restype = ctypes.c_int
# int rename(const char* old_filename, const char* new_filename)
dll.rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.rename.restype = ctypes.c_int
# void rewind(FILE* stream)
dll.rewind.argtypes = (ctypes.c_void_p,)
dll.rewind.restype = None
# void setbuf(FILE* stream, char* buffer)
dll.setbuf.argtypes = (ctypes.c_void_p, ctypes.c_char_p)
dll.setbuf.restype = None
# int setvbuf(FILE* stream, char* buffer, int mode, size_t size)
dll.setvbuf.argtypes = (ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_size_t)
dll.setvbuf.restype = ctypes.c_int
# FILE* tmpfile(void)
dll.tmpfile.argtypes = ()
dll.tmpfile.restype = ctypes.c_void_p
# char* tmpnam(char* str)
dll.tmpnam.argtypes = (ctypes.c_char_p,)
dll.tmpnam.restype = ctypes.c_char_p
# int fprintf(FILE* stream, const char* format, ...)
dll.fprintf.argtypes = (ctypes.c_void_p, ctypes.c_char_p)
dll.fprintf.restype = ctypes.c_int
# int printf(const char* format, ...)
dll.printf.argtypes = (ctypes.c_char_p,)
dll.printf.restype = ctypes.c_int
# int sprintf(char* str, const char* format, ...)
dll.sprintf.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.sprintf.restype = ctypes.c_int
# int vfprintf(FILE* stream, const char* format, va_list arg)
# int vprintf(const char* format, va_list arg)
# int vsprintf(char* str, const char* format, va_list arg)
# int fscanf(FILE* stream, const char* format, ...)
dll.fscanf.argtypes = (ctypes.c_void_p, ctypes.c_char_p)
dll.fscanf.restype = ctypes.c_int
# int scanf(const char* format, ...)
dll.scanf.argtypes = (ctypes.c_char_p,)
dll.scanf.restype = ctypes.c_int
# int sscanf(const char* str, const char* format, ...)
dll.sscanf.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.sscanf.restype = ctypes.c_int
# int fgetc(FILE* stream)
dll.fgetc.argtypes = (ctypes.c_void_p,)
dll.fgetc.restype = ctypes.c_int
# char* fgets(char* str, int n, FILE* stream)
dll.fgets.argtypes = (ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
dll.fgets.restype = ctypes.c_char_p
# int fputc(int char, FILE* stream)
dll.fputc.argtypes = (ctypes.c_char, ctypes.c_void_p)
dll.fputc.restype = ctypes.c_int
# int fputs(const char* str, FILE* stream)
dll.fputs.argtypes = (ctypes.c_char_p, ctypes.c_void_p)
dll.fputs.restype = ctypes.c_int
# int getc(FILE* stream)
dll.getc.argtypes = (ctypes.c_void_p,)
dll.getc.restype = ctypes.c_int
# int getchar(void)
dll.getchar.argtypes = ()
dll.getchar.restype = ctypes.c_int
# char* gets(char* str)
dll.gets.argtypes = (ctypes.c_char_p,)
dll.gets.restype = ctypes.c_char_p
# int putc(int char, FILE* stream)
dll.putc.argtypes = (ctypes.c_char, ctypes.c_void_p)
dll.putc.restype = ctypes.c_int
# int putchar(int char)
dll.putchar.argtypes = (ctypes.c_char,)
dll.putchar.restype = ctypes.c_int
# int puts(const char* str)
dll.puts.argtypes = (ctypes.c_char_p,)
dll.puts.restype = ctypes.c_int
# int ungetc(int char, FILE* stream)
dll.ungetc.argtypes = (
    ctypes.c_char,
    ctypes.c_void_p,
)
dll.ungetc.restype = ctypes.c_int
# void perror(const char* str)
dll.perror.argtypes = (ctypes.c_char_p,)
dll.perror.restype = None
# double strtod(const char* str, char** endptr)
dll.strtod.argtypes = (ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p))
dll.strtod.restype = ctypes.c_double
# long int strtol(const char* str, char** endptr, int base)
dll.strtol.argtypes = (ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_int)
dll.strtol.restype = ctypes.c_long
# unsigned long int strtoul(const char* str, char** endptr, int base)
dll.strtoul.argtypes = (ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_int)
dll.strtoul.restype = ctypes.c_ulong
# void abort(void)
dll.abort.argtypes = ()
dll.abort.restype = None
# void exit(int status)
dll.exit.argtypes = (ctypes.c_int,)
dll.exit.restype = None
# char* getenv(const char* name)
dll.getenv.argtypes = (ctypes.c_char_p,)
dll.getenv.restype = ctypes.c_char_p
# int system(const char* string)
dll.system.argtypes = (ctypes.c_char_p,)
dll.system.restype = ctypes.c_int
# void* bsearch(const void* key, const void* base, size_t nitems, size_t size, int (*compar)(const void* , const void* ))
# void qsort(void* base, size_t nitems, size_t size, int (*compar)(const void* , const void*))
# int abs(int x)
dll.abs.argtypes = (ctypes.c_int,)
dll.abs.restype = ctypes.c_int
# long int labs(long int x)
dll.labs.argtypes = (ctypes.c_long,)
dll.labs.restype = ctypes.c_long
# int rand(void)
dll.rand.argtypes = ()
dll.rand.restype = ctypes.c_int
# void srand(unsigned int seed)
dll.srand.argtypes = (ctypes.c_long,)
dll.srand.restype = None
# int mblen(const char* str, size_t n)
dll.mblen.argtypes = (ctypes.c_char_p, ctypes.c_size_t)
dll.mblen.restype = ctypes.c_int
# size_t mbstowcs(wchar_t* pwcs, const char* str, size_t n)
dll.mbstowcs.argtypes = (ctypes.c_wchar_p, ctypes.c_char_p, ctypes.c_size_t)
dll.mbstowcs.restype = ctypes.c_size_t
# int mbtowc(wchar_t* pwc, const char* str, size_t n)
dll.mbtowc.argtypes = (ctypes.c_wchar_p, ctypes.c_char_p, ctypes.c_size_t)
dll.mbtowc.restype = ctypes.c_int
# size_t wcstombs(char* str, const wchar_t* pwcs, size_t n)
dll.wcstombs.argtypes = (ctypes.c_char_p, ctypes.c_wchar_p, ctypes.c_size_t)
dll.wcstombs.restype = ctypes.c_size_t
# int wctomb(char* str, wchar_t wchar)
dll.wctomb.argtypes = (ctypes.c_char_p, ctypes.c_wchar_p)
dll.wctomb.restype = ctypes.c_int
# void* memchr(const void* str, int c, size_t n)
dll.memchr.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t)
dll.memchr.restype = ctypes.c_void_p
# int memcmp(const void* str1, const void* str2, size_t n)
dll.memcmp.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)
dll.memcmp.restype = ctypes.c_int
# void* memcpy(void* dest, const void* src, size_t n)
dll.memcpy.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)
dll.memcpy.restype = ctypes.c_void_p
# void* memmove(void* dest, const void* src, size_t n)
dll.memmove.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)
dll.memmove.restype = ctypes.c_void_p
# void* memset(void* str, int c, size_t n)
dll.memset.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t)
dll.memset.restype = ctypes.c_void_p
# char* strcat(char* dest, const char* src)
dll.strcat.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strcat.restype = ctypes.c_char_p
# char* strncat(char* dest, const char* src, size_t n)
dll.strncat.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t)
dll.strncat.restype = ctypes.c_char_p
# char* strchr(const char* str, int c)
dll.strchr.argtypes = (ctypes.c_char_p, ctypes.c_int)
dll.strchr.restype = ctypes.c_char_p
# int strcmp(const char* str1, const char* str2)
dll.strcmp.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strcmp.restype = ctypes.c_int
# int strncmp(const char* str1, const char* str2, size_t n)
dll.strncmp.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strncmp.restype = ctypes.c_int
# int strcoll(const char* str1, const char* str2)
dll.strcoll.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strcoll.restype = ctypes.c_int
# char* strcpy(char* dest, const char* src)
dll.strcpy.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strcpy.restype = ctypes.c_char_p
# char* strncpy(char* dest, const char* src, size_t n)
dll.strncpy.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t)
dll.strncpy.restype = ctypes.c_char_p
# size_t strcspn(const char* str1, const char* str2)
dll.strcspn.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strcspn.restype = ctypes.c_size_t
# char* strerror(int errnum)
dll.strerror.argtypes = (ctypes.c_int,)
dll.strerror.restype = ctypes.c_char_p
# size_t strlen(const char* str)
dll.strlen.argtypes = (ctypes.c_char_p,)
dll.strlen.restype = ctypes.c_size_t
# char* strpbrk(const char* str1, const char* str2)
dll.strpbrk.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strpbrk.restype = ctypes.c_char_p
# char* strrchr(const char* str, int c)
dll.strrchr.argtypes = (ctypes.c_char_p, ctypes.c_int)
dll.strrchr.restype = ctypes.c_char_p
# size_t strspn(const char* str1, const char* str2)
dll.strspn.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strspn.restype = ctypes.c_size_t
# char* strstr(const char* haystack, const char* needle)
dll.strstr.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strstr.restype = ctypes.c_char_p
# char* strtok(char* str, const char* delim)
dll.strstr.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strtok.restype = ctypes.c_char_p
# size_t strxfrm(char* dest, const char* src, size_t n)
dll.strxfrm.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t)
dll.strxfrm.restype = ctypes.c_size_t
# char* asctime(const struct tm* timeptr)
dll.asctime.argtypes = (ctypes.POINTER(tm),)
dll.asctime.restype = ctypes.c_char_p
# clock_t clock(void)
dll.clock.argtypes = ()
dll.clock.restype = ctypes.c_int
# char* ctime(const time_t* timer)
dll.ctime.argtypes = (ctypes.POINTER(ctypes.c_int),)
dll.ctime.restype = ctypes.c_char_p
# double difftime(time_t time1, time_t time2)
dll.difftime.argtypes = (ctypes.c_int, ctypes.c_int)
dll.difftime.restype = ctypes.c_double
# time_t mktime(struct tm* timeptr)
dll.mktime.argtypes = (ctypes.POINTER(tm),)
dll.mktime.restype = ctypes.c_int
# size_t strftime(char *str, size_t maxsize, const char *format, const struct tm* timeptr)
dll.strftime.argtypes = (ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.POINTER(tm),)
dll.strftime.restype = ctypes.c_size_t
# time_t time(time_t* timer)
dll.time.argtypes = (ctypes.POINTER(ctypes.c_int),)
dll.time.restype = ctypes.c_int"""
main(string)
