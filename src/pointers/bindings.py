from ._cstd import *
from ._cstd import tm
from typing import Any, Union
from .c_pointer import CVoidPointer, CTypedPointer, StructPointer
import ctypes


def _base(fn: "ctypes._NamedFuncPointer", *args) -> Any:
    res = fn(*args)
    res_typ = type(res)

    if res_typ.__name__.startswith("LP_"):
        res = (
            CTypedPointer(
                ctypes.addressof(res),
                res_typ,
            )
            if not issubclass(type(res.contents), ctypes.Structure)
            else StructPointer(ctypes.addressof(res.contents), res_typ)
        )

    elif fn.restype is ctypes.c_void_p:  # type safety gets mad if i dont use elif here
        res = CVoidPointer(res)

    return res


def _make_char_pointer(data: Union[str, bytes]) -> bytes:
    return data if isinstance(data, bytes) else data.encode()


def isalnum(c: int) -> int:
    return _base(dll.isalnum, c)


def isalpha(c: int) -> int:
    return _base(dll.isalpha, c)


def iscntrl(c: int) -> int:
    return _base(dll.iscntrl, c)


def isdigit(c: int) -> int:
    return _base(dll.isdigit, c)


def isgraph(c: int) -> int:
    return _base(dll.isgraph, c)


def islower(c: int) -> int:
    return _base(dll.islower, c)


def isprint(c: int) -> int:
    return _base(dll.isprint, c)


def ispunct(c: int) -> int:
    return _base(dll.ispunct, c)


def isspace(c: int) -> int:
    return _base(dll.isspace, c)


def isupper(c: int) -> int:
    return _base(dll.isupper, c)


def isxdigit(c: int) -> int:
    return _base(dll.isxdigit, c)


def tolower(c: int) -> int:
    return _base(dll.tolower, c)


def toupper(c: int) -> int:
    return _base(dll.toupper, c)


def setlocale(category: int, locale: str) -> str:
    return _base(dll.setlocale, category, _make_char_pointer(locale))


def frexp(x: float, exponent: CTypedPointer[int]) -> int:
    return _base(dll.frexp, x, exponent)


def ldexp(x: float, exponent: int) -> int:
    return _base(dll.ldexp, x, exponent)


def modf(x: float, integer: CTypedPointer[float]) -> int:
    return _base(dll.modf, x, integer)


def fclose(stream: CVoidPointer) -> int:
    return _base(dll.fclose, stream)


def clearerr(stream: CVoidPointer) -> None:
    return _base(dll.clearerr, stream)


def feof(stream: CVoidPointer) -> int:
    return _base(dll.feof, stream)


def ferror(stream: CVoidPointer) -> int:
    return _base(dll.ferror, stream)


def fflush(stream: CVoidPointer) -> int:
    return _base(dll.fflush, stream)


def fgetpos(stream: CVoidPointer, pos: CVoidPointer) -> int:
    return _base(dll.fgetpos, stream, pos)


def fopen(filename: str, mode: str) -> CVoidPointer:
    return _base(dll.fopen, _make_char_pointer(filename), _make_char_pointer(mode))


def fread(ptr: CTypedPointer[Any], size: int, nmemb: int, stream: CVoidPointer) -> int:
    return _base(dll.fread, ptr, size, nmemb, stream)


def freopen(filename: str, mode: str, stream: CVoidPointer) -> CVoidPointer:
    return _base(
        dll.freopen, _make_char_pointer(filename), _make_char_pointer(mode), stream
    )


def fseek(stream: CVoidPointer, offset: int, whence: int) -> int:
    return _base(dll.fseek, stream, offset, whence)


def fsetpos(stream: CVoidPointer, pos: CVoidPointer) -> int:
    return _base(dll.fsetpos, stream, pos)


def ftell(stream: CVoidPointer) -> int:
    return _base(dll.ftell, stream)


def fwrite(ptr: CTypedPointer[Any], size: int, nmemb: int, stream: CVoidPointer) -> int:
    return _base(dll.fwrite, ptr, size, nmemb, stream)


def remove(filename: str) -> int:
    return _base(dll.remove, _make_char_pointer(filename))


def rename(old_filename: str, new_filename: str) -> int:
    return _base(
        dll.rename, _make_char_pointer(old_filename), _make_char_pointer(new_filename)
    )


def rewind(stream: CVoidPointer) -> None:
    return _base(dll.rewind, stream)


def setbuf(stream: CVoidPointer, buffer: str) -> None:
    return _base(dll.setbuf, stream, _make_char_pointer(buffer))


def setvbuf(stream: CVoidPointer, buffer: str, mode: int, size: int) -> int:
    return _base(dll.setvbuf, stream, _make_char_pointer(buffer), mode, size)


def tmpfile() -> CVoidPointer:
    return _base(dll.tmpfile)


def tmpnam(string: str) -> str:
    return _base(dll.tmpnam, _make_char_pointer(string))


def fprintf(stream: CVoidPointer, fmt: str, *args: str) -> int:
    return _base(dll.fprintf, stream, _make_char_pointer(fmt), *args)


def printf(fmt: str, *args: str) -> int:
    return _base(dll.printf, _make_char_pointer(fmt), *args)


def sprintf(string: str, fmt: str, *args: str) -> int:
    return _base(
        dll.sprintf, _make_char_pointer(string), _make_char_pointer(fmt), *args
    )


def fscanf(stream: CVoidPointer, fmt: str, *args: str) -> int:
    return _base(dll.fscanf, stream, _make_char_pointer(fmt), *args)


def scanf(fmt: str, *args: str) -> int:
    return _base(dll.scanf, _make_char_pointer(fmt), *args)


def sscanf(string: str, fmt: str, *args: str) -> int:
    return _base(dll.sscanf, _make_char_pointer(string), _make_char_pointer(fmt), *args)


def fgetc(stream: CVoidPointer) -> int:
    return _base(dll.fgetc, stream)


def fgets(string: str, n: int, stream: CVoidPointer) -> str:
    return _base(dll.fgets, _make_char_pointer(string), n, stream)


def fputc(char: int, stream: CVoidPointer) -> int:
    return _base(dll.fputc, char, stream)


def fputs(string: str, stream: CVoidPointer) -> int:
    return _base(dll.fputs, _make_char_pointer(string), stream)


def getc(stream: CVoidPointer) -> int:
    return _base(dll.getc, stream)


def getchar() -> int:
    return _base(dll.getchar)


def gets(string: str) -> str:
    return _base(dll.gets, _make_char_pointer(string))


def putc(char: int, stream: CVoidPointer) -> int:
    return _base(dll.putc, char, stream)


def putchar(char: int) -> int:
    return _base(dll.putchar, char)


def puts(string: str) -> int:
    return _base(dll.puts, _make_char_pointer(string))


def ungetc(char: int, stream: CVoidPointer) -> int:
    return _base(dll.ungetc, char, stream)


def perror(string: str) -> None:
    return _base(dll.perror, _make_char_pointer(string))


def strtod(string: str, endptr: CTypedPointer[str]) -> int:
    return _base(dll.strtod, _make_char_pointer(string), endptr)


def strtol(string: str, endptr: CTypedPointer[str], base: int) -> int:
    return _base(dll.strtol, _make_char_pointer(string), endptr, base)


def strtoul(string: str, endptr: CTypedPointer[str], base: int) -> int:
    return _base(dll.strtoul, _make_char_pointer(string), endptr, base)


def abort() -> None:
    return _base(dll.abort)


def exit(status: int) -> None:
    return _base(dll.exit, status)


def getenv(name: str) -> str:
    return _base(dll.getenv, _make_char_pointer(name))


def system(string: str) -> int:
    return _base(dll.system, _make_char_pointer(string))


def abs(x: int) -> int:
    return _base(dll.abs, x)


def labs(x: int) -> int:
    return _base(dll.labs, x)


def rand() -> int:
    return _base(dll.rand)


def srand(seed: int) -> None:
    return _base(dll.srand, seed)


def mblen(string: str, n: int) -> int:
    return _base(dll.mblen, _make_char_pointer(string), n)


def mbstowcs(pwcs: str, string: str, n: int) -> int:
    return _base(dll.mbstowcs, pwcs, _make_char_pointer(string), n)


def mbtowc(pwc: str, string: str, n: int) -> int:
    return _base(dll.mbtowc, pwc, _make_char_pointer(string), n)


def wcstombs(string: str, pwcs: str, n: int) -> int:
    return _base(dll.wcstombs, _make_char_pointer(string), pwcs, n)


def wctomb(string: str, wchar: str) -> int:
    return _base(dll.wctomb, _make_char_pointer(string), wchar)


def memchr(string: CTypedPointer[Any], c: int, n: int) -> CVoidPointer:
    return _base(dll.memchr, string, c, n)


def memcmp(str1: CTypedPointer[Any], str2: CTypedPointer[Any], n: int) -> int:
    return _base(dll.memcmp, str1, str2, n)


def memcpy(dest: CTypedPointer[Any], src: CTypedPointer[Any], n: int) -> CVoidPointer:
    return _base(dll.memcpy, dest, src, n)


def memmove(dest: CTypedPointer[Any], src: CTypedPointer[Any], n: int) -> CVoidPointer:
    return _base(dll.memmove, dest, src, n)


def memset(string: CTypedPointer[Any], c: int, n: int) -> CVoidPointer:
    return _base(dll.memset, string, c, n)


def strcat(dest: str, src: str) -> str:
    return _base(dll.strcat, _make_char_pointer(dest), _make_char_pointer(src))


def strncat(dest: str, src: str, n: int) -> str:
    return _base(dll.strncat, _make_char_pointer(dest), _make_char_pointer(src), n)


def strchr(string: str, c: int) -> str:
    return _base(dll.strchr, _make_char_pointer(string), c)


def strcmp(str1: str, str2: str) -> int:
    return _base(dll.strcmp, _make_char_pointer(str1), _make_char_pointer(str2))


def strncmp(str1: str, str2: str, n: int) -> int:
    return _base(dll.strncmp, _make_char_pointer(str1), _make_char_pointer(str2), n)


def strcoll(str1: str, str2: str) -> int:
    return _base(dll.strcoll, _make_char_pointer(str1), _make_char_pointer(str2))


def strcpy(dest: str, src: str) -> str:
    return _base(dll.strcpy, _make_char_pointer(dest), _make_char_pointer(src))


def strncpy(dest: str, src: str, n: int) -> str:
    return _base(dll.strncpy, _make_char_pointer(dest), _make_char_pointer(src), n)


def strcspn(str1: str, str2: str) -> int:
    return _base(dll.strcspn, _make_char_pointer(str1), _make_char_pointer(str2))


def strerror(errnum: int) -> str:
    return _base(dll.strerror, errnum)


def strlen(string: str) -> int:
    return _base(dll.strlen, _make_char_pointer(string))


def strpbrk(str1: str, str2: str) -> str:
    return _base(dll.strpbrk, _make_char_pointer(str1), _make_char_pointer(str2))


def strrchr(string: str, c: int) -> str:
    return _base(dll.strrchr, _make_char_pointer(string), c)


def strspn(str1: str, str2: str) -> int:
    return _base(dll.strspn, _make_char_pointer(str1), _make_char_pointer(str2))


def strstr(haystack: str, needle: str) -> str:
    return _base(dll.strstr, _make_char_pointer(haystack), _make_char_pointer(needle))


def strtok(string: str, delim: str) -> str:
    return _base(dll.strtok, _make_char_pointer(string), _make_char_pointer(delim))


def strxfrm(dest: str, src: str, n: int) -> int:
    return _base(dll.strxfrm, _make_char_pointer(dest), _make_char_pointer(src), n)


def asctime(timeptr: StructPointer[tm]) -> str:
    return _base(dll.asctime, timeptr)


def clock() -> int:
    return _base(dll.clock)


def ctime(timer: CTypedPointer[int]) -> str:
    return _base(dll.ctime, timer)


def difftime(time1: int, time2: int) -> int:
    return _base(dll.difftime, time1, time2)


def mktime(timeptr: StructPointer[tm]) -> int:
    return _base(dll.mktime, timeptr)


def strftime(
    string: str, maxsize: int, fmt: CTypedPointer[str], timeptr: StructPointer[tm]
) -> int:
    return _base(dll.strftime, string, maxsize, fmt, timeptr)


def time(timer: CTypedPointer[int]) -> int:
    return _base(dll.time, timer)
