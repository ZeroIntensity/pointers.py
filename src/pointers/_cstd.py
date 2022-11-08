import ctypes
from ctypes.util import find_library
from sys import platform

__all__ = (
    "c_malloc",
    "c_free",
    "c_realloc",
    "c_calloc",
    "dll",
    "tm",
    "lconv",
    "div_t",
    "ldiv_t",
)

_c_library_name: str

if platform in ("win32", "cygwin"):
    _c_library_name = "msvcrt"
elif platform == "darwin":
    _c_library_name = "libc.dylib"
else:
    _c_library_name = find_library("c") or "libc.so.6"

dll = ctypes.CDLL(_c_library_name)


class tm(ctypes.Structure):
    _fields_ = [
        ("tm_sec", ctypes.c_int),
        ("tm_min", ctypes.c_int),
        ("tm_hour", ctypes.c_int),
        ("tm_mday", ctypes.c_int),
        ("tm_mon", ctypes.c_int),
        ("tm_year", ctypes.c_int),
        ("tm_wday", ctypes.c_int),
        ("tm_yday", ctypes.c_int),
        ("tm_isdst", ctypes.c_int),
    ]


class div_t(ctypes.Structure):
    _fields_ = [
        ("quot", ctypes.c_int),
        ("rem", ctypes.c_int),
    ]


class ldiv_t(ctypes.Structure):
    _fields_ = [
        ("quot", ctypes.c_long),
        ("rem", ctypes.c_long),
    ]


class lconv(ctypes.Structure):
    _fields_ = [
        ("decimal_point", ctypes.c_char_p),
        ("thousands_sep", ctypes.c_char_p),
        ("grouping", ctypes.c_char_p),
        ("int_curr_symbol", ctypes.c_char_p),
        ("currency_symbol", ctypes.c_char_p),
        ("mon_decimal_point", ctypes.c_char_p),
        ("mon_thousands_sep", ctypes.c_char_p),
        ("mon_grouping", ctypes.c_char_p),
        ("positive_sign", ctypes.c_char_p),
        ("negative_sign", ctypes.c_char_p),
        ("int_frac_digits", ctypes.c_char),
        ("frac_digits", ctypes.c_char),
        ("p_cs_precedes", ctypes.c_char),
        ("p_sep_by_space", ctypes.c_char),
        ("n_sep_by_space", ctypes.c_char),
        ("p_sign_posn", ctypes.c_char),
        ("n_sign_posn", ctypes.c_char),
    ]


c_raise = getattr(dll, "raise")

# void* malloc(size_t size);
dll.malloc.argtypes = (ctypes.c_size_t,)
dll.malloc.restype = ctypes.c_void_p
# void free(void* ptr);
dll.free.argtypes = (ctypes.c_void_p,)
dll.free.restype = None
# void* realloc(void* ptr, size_t size);
dll.realloc.argtypes = (ctypes.c_void_p, ctypes.c_size_t)
dll.realloc.restype = ctypes.c_void_p
# void* calloc (size_t num, size_t size);
dll.calloc.argtypes = (ctypes.c_size_t, ctypes.c_size_t)
dll.calloc.restype = ctypes.c_void_p
# int isalnum(int c)
dll.isalnum.argtypes = (ctypes.c_char,)
dll.isalnum.restype = ctypes.c_int
# int isalpha(int c)
dll.isalpha.argtypes = (ctypes.c_char,)
dll.isalpha.restype = ctypes.c_int
# int iscntrl(int c)
dll.iscntrl.argtypes = (ctypes.c_char,)
dll.iscntrl.restype = ctypes.c_int
# int isdigit(int c)
dll.isdigit.argtypes = (ctypes.c_char,)
dll.isdigit.restype = ctypes.c_int
# int isgraph(int c)
dll.isgraph.argtypes = (ctypes.c_char,)
dll.isgraph.restype = ctypes.c_int
# int islower(int c)
dll.islower.argtypes = (ctypes.c_char,)
dll.islower.restype = ctypes.c_int
# int isprint(int c)
dll.isprint.argtypes = (ctypes.c_char,)
dll.isprint.restype = ctypes.c_int
# int ispunct(int c)
dll.ispunct.argtypes = (ctypes.c_char,)
dll.ispunct.restype = ctypes.c_int
# int isspace(int c)
dll.isspace.argtypes = (ctypes.c_char,)
dll.isspace.restype = ctypes.c_int
# int isupper(int c)
dll.isupper.argtypes = (ctypes.c_char,)
dll.isupper.restype = ctypes.c_int
# int isxdigit(int c)
dll.isxdigit.argtypes = (ctypes.c_char,)
dll.isxdigit.restype = ctypes.c_int
# int tolower(int c)
dll.tolower.argtypes = (ctypes.c_char,)
dll.tolower.restype = ctypes.c_char
# int toupper(int c)
dll.toupper.argtypes = (ctypes.c_char,)
dll.toupper.restype = ctypes.c_char
# char* setlocale(int category, const char* locale)
dll.setlocale.argtypes = (ctypes.c_int, ctypes.c_char_p)
dll.setlocale.restype = ctypes.c_char_p
# struct lconv* localeconv(void)
dll.localeconv.argtypes = ()
dll.localeconv.restype = ctypes.POINTER(lconv)
# double frexp(double x, int* exponent)
dll.frexp.argtypes = (
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_int),
)
dll.frexp.restype = ctypes.c_double
# double ldexp(double x, int exponent)
dll.ldexp.argtypes = (ctypes.c_double, ctypes.c_int)
dll.ldexp.restype = ctypes.c_double
# double modf(double x, double* integer)
dll.modf.argtypes = (
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_double),
)
dll.modf.restype = ctypes.c_double
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
dll.fread.argtypes = (
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_size_t,
)
dll.fread.restype = ctypes.c_size_t
# FILE* freopen(const char* filename, const char* mode, FILE* stream)
dll.freopen.argtypes = (
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_void_p,
)
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
dll.setvbuf.argtypes = (
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_size_t,
)
dll.setvbuf.restype = ctypes.c_int
# FILE* tmpfile(void)
dll.tmpfile.argtypes = ()
dll.tmpfile.restype = ctypes.c_void_p
# char* tmpnam(char* str)
dll.tmpnam.argtypes = (ctypes.c_char_p,)
dll.tmpnam.restype = ctypes.c_char_p
# int fprintf(FILE* stream, const char* format, ...)
dll.fprintf.restype = ctypes.c_int
# int printf(const char* format, ...)
dll.printf.restype = ctypes.c_int
# int sprintf(char* str, const char* format, ...)
dll.sprintf.restype = ctypes.c_int
# int vfprintf(FILE* stream, const char* format, va_list arg)
# int vprintf(const char* format, va_list arg)
# int vsprintf(char* str, const char* format, va_list arg)
# int fscanf(FILE* stream, const char* format, ...)
dll.fscanf.restype = ctypes.c_int
# int scanf(const char* format, ...)
dll.scanf.argtypes = (ctypes.c_char_p,)
dll.scanf.restype = ctypes.c_int
# int sscanf(const char* str, const char* format, ...)
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
dll.strtol.argtypes = (
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.c_int,
)
dll.strtol.restype = ctypes.c_long
# unsigned long int strtoul(const char* str, char** endptr, int base)
dll.strtoul.argtypes = (
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.c_int,
)
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
# int abs(int x)
dll.abs.argtypes = (ctypes.c_int,)
dll.abs.restype = ctypes.c_int
# div_t div(int numer, int denom)
dll.div.argtypes = (ctypes.c_int, ctypes.c_int)
dll.div.restype = div_t
# long int labs(long int x)
dll.labs.argtypes = (ctypes.c_long,)
dll.labs.restype = ctypes.c_long
# ldiv_t ldiv(long int numer, long int denom)
dll.ldiv.argtypes = (ctypes.c_long, ctypes.c_long)
dll.ldiv.restype = ldiv_t
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
dll.mbstowcs.argtypes = (
    ctypes.c_wchar_p,
    ctypes.c_char_p,
    ctypes.c_size_t,
)
dll.mbstowcs.restype = ctypes.c_size_t
# int mbtowc(wchar_t* pwc, const char* str, size_t n)
dll.mbtowc.argtypes = (
    ctypes.c_wchar_p,
    ctypes.c_char_p,
    ctypes.c_size_t,
)
dll.mbtowc.restype = ctypes.c_int
# size_t wcstombs(char* str, const wchar_t* pwcs, size_t n)
dll.wcstombs.argtypes = (
    ctypes.c_char_p,
    ctypes.c_wchar_p,
    ctypes.c_size_t,
)
dll.wcstombs.restype = ctypes.c_size_t
# int wctomb(char* str, wchar_t wchar)
dll.wctomb.argtypes = (ctypes.c_char_p, ctypes.c_wchar_p)
dll.wctomb.restype = ctypes.c_int
# void* memchr(const void* str, int c, size_t n)
dll.memchr.argtypes = (
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_size_t,
)
dll.memchr.restype = ctypes.c_void_p
# int memcmp(const void* str1, const void* str2, size_t n)
dll.memcmp.argtypes = (
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
)
dll.memcmp.restype = ctypes.c_int
# void* memcpy(void* dest, const void* src, size_t n)
dll.memcpy.argtypes = (
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
)
dll.memcpy.restype = ctypes.c_void_p
# void* memmove(void* dest, const void* src, size_t n)
dll.memmove.argtypes = (
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
)
dll.memmove.restype = ctypes.c_void_p
# void* memset(void* str, int c, size_t n)
dll.memset.argtypes = (
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_size_t,
)
dll.memset.restype = ctypes.c_void_p
# char* strcat(char* dest, const char* src)
dll.strcat.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
dll.strcat.restype = ctypes.c_char_p
# char* strncat(char* dest, const char* src, size_t n)
dll.strncat.argtypes = (
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_size_t,
)
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
dll.strncpy.argtypes = (
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_size_t,
)
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
dll.strxfrm.argtypes = (
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_size_t,
)
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
# struct tm* gmtime(const time_t* timer)
dll.gmtime.argtypes = (ctypes.POINTER(ctypes.c_int),)
dll.gmtime.restype = ctypes.POINTER(tm)
# struct tm* localtime(const time_t* timer)
dll.localtime.argtypes = (ctypes.c_int,)
dll.localtime.restype = ctypes.POINTER(tm)
# time_t mktime(struct tm* timeptr)
dll.mktime.argtypes = (ctypes.POINTER(tm),)
dll.mktime.restype = ctypes.c_int
# size_t strftime(
#   char *str,
#   size_t maxsize,
#   const char *format,
#   const struct tm* timeptr
# )
dll.strftime.argtypes = (
    ctypes.c_char_p,
    ctypes.c_size_t,
    ctypes.c_char_p,
    ctypes.POINTER(tm),
)
dll.strftime.restype = ctypes.c_size_t
# time_t time(time_t* timer)
dll.time.argtypes = (ctypes.POINTER(ctypes.c_int),)
dll.time.restype = ctypes.c_int
# void (*signal(int sig, void (*func)(int)))(int)
dll.signal.argtypes = (ctypes.c_int, ctypes.CFUNCTYPE(None, ctypes.c_int))
dll.signal.restype = None
# void qsort(
#   void *base,
#   size_t nitems,
#   size_t size,
#   int (*compar)(const void *, const void*)
# )
dll.qsort.argtypes = (
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_size_t,
    ctypes.CFUNCTYPE(
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ),
)
dll.qsort.restype = None
# void *bsearch(
#     const void *key,
#     const void *base,
#     size_t nitems,
#     size_t size,
#     int (*compar)(const void *, const void *)
# )
dll.bsearch.argtypes = (
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_size_t,
    ctypes.CFUNCTYPE(
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ),
)
dll.bsearch.restype = ctypes.c_void_p

c_malloc = dll.malloc
c_free = dll.free
c_realloc = dll.realloc
c_calloc = dll.calloc
