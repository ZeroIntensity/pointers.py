from ._cstd import (
    dll,
    DivT,
    Tm,
    LDivT,
    Lconv,
    STRUCT_MAP,
    c_raise as ct_raise,
    c_malloc as _malloc,
    c_calloc as _calloc,
    c_realloc as _realloc,
    c_free as _free,
)
from typing import (
    Any,
    Union,
    TypeVar,
    Optional,
    TYPE_CHECKING,
    Dict,
    Type,
    Iterator,
    Tuple,
)
from .c_pointer import (
    VoidPointer,
    TypedCPointer,
    StructPointer,
    _BaseCPointer,
)
import ctypes
from . import _cstd
from .exceptions import InvalidBindingParameter

if TYPE_CHECKING:
    from .struct import Struct

T = TypeVar("T")
PointerLike = Union[TypedCPointer[Any], VoidPointer]
StringLike = Union[str, bytes, VoidPointer, TypedCPointer[bytes]]
Format = Union[str, bytes, PointerLike]

__all__ = (
    "isalnum",
    "isalpha",
    "iscntrl",
    "isdigit",
    "isgraph",
    "islower",
    "isprint",
    "ispunct",
    "isspace",
    "isupper",
    "isxdigit",
    "tolower",
    "toupper",
    "setlocale",
    "frexp",
    "ldexp",
    "modf",
    "fclose",
    "clearerr",
    "feof",
    "ferror",
    "fflush",
    "fgetpos",
    "fopen",
    "fread",
    "freopen",
    "fseek",
    "fsetpos",
    "ftell",
    "fwrite",
    "remove",
    "rename",
    "rewind",
    "setbuf",
    "setvbuf",
    "tmpfile",
    "tmpnam",
    "fprintf",
    "printf",
    "sprintf",
    "fscanf",
    "scanf",
    "sscanf",
    "fgetc",
    "fgets",
    "fputc",
    "fputs",
    "getc",
    "getchar",
    "gets",
    "putc",
    "putchar",
    "puts",
    "ungetc",
    "perror",
    "strtod",
    "strtol",
    "strtoul",
    "abort",
    "exit",
    "getenv",
    "system",
    "abs",
    "labs",
    "rand",
    "srand",
    "mblen",
    "mbstowcs",
    "mbtowc",
    "wcstombs",
    "wctomb",
    "memchr",
    "memcmp",
    "memcpy",
    "memmove",
    "memset",
    "strcat",
    "strncat",
    "strchr",
    "strcmp",
    "strncmp",
    "strcoll",
    "strcpy",
    "strncpy",
    "strcspn",
    "strerror",
    "strlen",
    "strpbrk",
    "strrchr",
    "strspn",
    "strstr",
    "strtok",
    "strxfrm",
    "asctime",
    "clock",
    "ctime",
    "difftime",
    "mktime",
    "strftime",
    "time",
    "div",
    "ldiv",
    "localeconv",
    "c_raise",
    "c_malloc",
    "c_calloc",
    "c_realloc",
    "c_free",
    "gmtime",
)


def _not_null(data: Optional[T]) -> T:
    assert data is not None
    return data


StructMap = Dict[Type[ctypes.Structure], Type["Struct"]]


def _decode_response(
    res: Any,
    struct_map: StructMap,
    fn: "ctypes._NamedFuncPointer",
) -> Any:
    res_typ = type(res)

    if res_typ.__name__.startswith("LP_"):
        struct_type = struct_map.get(getattr(_cstd, res_typ.__name__[3:]))
        struct = (
            struct_type.from_existing(res.contents) if struct_type else None
        )  # fmt: off

        res = (
            TypedCPointer(ctypes.addressof(res), res_typ, ctypes.sizeof(res))
            if not issubclass(type(res.contents), ctypes.Structure)
            else StructPointer(id(struct), type(_not_null(struct)), struct)
        )
    # type safety gets mad if i dont use elif here
    elif fn.restype is ctypes.c_void_p:
        res = VoidPointer(res, ctypes.sizeof(ctypes.c_void_p(res)))

    elif issubclass(res_typ, ctypes.Structure):
        struct = struct_map.get(res_typ)
        if struct:
            res = struct.from_existing(res)

    return res


def _validate_args(
    args: Tuple[Any, ...],
    fn: "ctypes._NamedFuncPointer",
) -> None:
    if not fn.argtypes:
        return

    for index, (value, typ) in enumerate(zip(args, fn.argtypes)):
        n_type = VoidPointer.get_py(typ)

        if not isinstance(value, n_type):
            v_type = type(value)

            if ((v_type is ctypes.c_char_p) and (n_type is bytes)) or (
                issubclass(v_type, _BaseCPointer) and (typ is ctypes.c_void_p)
            ):
                continue

            raise InvalidBindingParameter(
                f"argument {index + 1} got invalid type: expected {n_type.__name__}, got {v_type.__name__}"  # noqa
            )


def _base(
    fn: "ctypes._NamedFuncPointer",
    *args,
    map_extra: Optional[StructMap] = None,
) -> Any:
    _validate_args(args, fn)
    res = fn(*args)

    return _decode_response(
        res,
        {**STRUCT_MAP, **(map_extra or {})},
        fn,
    )


def _make_char_pointer(data: StringLike) -> Union[bytes, ctypes.c_char_p]:
    if type(data) not in {VoidPointer, str, bytes, TypedCPointer}:
        raise InvalidBindingParameter(
            f"expected a string-like object, got {repr(data)}"  # noqa
        )

    if isinstance(data, bytes):
        return data

    is_typed_ptr: bool = isinstance(data, TypedCPointer)

    if isinstance(data, VoidPointer) or isinstance(data, TypedCPointer):
        # mypy is forcing me to call this twice
        if is_typed_ptr and (data.type is not bytes):
            raise InvalidBindingParameter(
                f"{data} does not point to bytes",
            )

        return ctypes.c_char_p(data.address)

    return data.encode()


def _make_format(*args: Format) -> Iterator[Format]:
    for i in args:
        for x in {VoidPointer, str, bytes}:
            if isinstance(i, x):
                yield _make_char_pointer(i)  # type: ignore
                continue

        yield i


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


def setlocale(category: int, locale: StringLike) -> str:
    return _base(dll.setlocale, category, _make_char_pointer(locale))


def frexp(x: float, exponent: TypedCPointer[int]) -> int:
    return _base(dll.frexp, x, exponent)


def ldexp(x: float, exponent: int) -> int:
    return _base(dll.ldexp, x, exponent)


def modf(x: float, integer: TypedCPointer[float]) -> int:
    return _base(dll.modf, x, integer)


def fclose(stream: PointerLike) -> int:
    return _base(dll.fclose, stream)


def clearerr(stream: PointerLike) -> None:
    return _base(dll.clearerr, stream)


def feof(stream: PointerLike) -> int:
    return _base(dll.feof, stream)


def ferror(stream: PointerLike) -> int:
    return _base(dll.ferror, stream)


def fflush(stream: PointerLike) -> int:
    return _base(dll.fflush, stream)


def fgetpos(stream: PointerLike, pos: PointerLike) -> int:
    return _base(dll.fgetpos, stream, pos)


def fopen(filename: StringLike, mode: StringLike) -> VoidPointer:
    return _base(
        dll.fopen,
        _make_char_pointer(filename),
        _make_char_pointer(mode),
    )


def fread(
    ptr: TypedCPointer[Any],
    size: int,
    nmemb: int,
    stream: PointerLike,
) -> int:
    return _base(dll.fread, ptr, size, nmemb, stream)


def freopen(
    filename: StringLike,
    mode: StringLike,
    stream: PointerLike,
) -> VoidPointer:
    return _base(
        dll.freopen,
        _make_char_pointer(filename),
        _make_char_pointer(mode),
        stream,
    )


def fseek(stream: PointerLike, offset: int, whence: int) -> int:
    return _base(dll.fseek, stream, offset, whence)


def fsetpos(stream: PointerLike, pos: PointerLike) -> int:
    return _base(dll.fsetpos, stream, pos)


def ftell(stream: PointerLike) -> int:
    return _base(dll.ftell, stream)


def fwrite(
    ptr: TypedCPointer[Any],
    size: int,
    nmemb: int,
    stream: PointerLike,
) -> int:
    return _base(dll.fwrite, ptr, size, nmemb, stream)


def remove(filename: StringLike) -> int:
    return _base(dll.remove, _make_char_pointer(filename))


def rename(old_filename: StringLike, new_filename: StringLike) -> int:
    return _base(
        dll.rename,
        _make_char_pointer(old_filename),
        _make_char_pointer(new_filename),
    )


def rewind(stream: PointerLike) -> None:
    return _base(dll.rewind, stream)


def setbuf(stream: PointerLike, buffer: StringLike) -> None:
    return _base(dll.setbuf, stream, _make_char_pointer(buffer))


def setvbuf(
    stream: PointerLike,
    buffer: str,
    mode: int,
    size: int,
) -> int:
    return _base(
        dll.setvbuf,
        stream,
        _make_char_pointer(buffer),
        mode,
        size,
    )


def tmpfile() -> VoidPointer:
    return _base(dll.tmpfile)


def tmpnam(string: str) -> str:
    return _base(dll.tmpnam, _make_char_pointer(string))


def fprintf(stream: PointerLike, fmt: StringLike, *args: Format) -> int:
    return _base(
        dll.fprintf,
        stream,
        _make_char_pointer(fmt),
        *_make_format(*args),
    )


def printf(fmt: StringLike, *args: Format) -> int:
    return _base(dll.printf, _make_char_pointer(fmt), *_make_format(*args))


def sprintf(string: StringLike, fmt: StringLike, *args: Format) -> int:
    return _base(
        dll.sprintf,
        _make_char_pointer(string),
        _make_char_pointer(fmt),
        *args,
    )


def fscanf(stream: PointerLike, fmt: StringLike, *args: Format) -> int:
    return _base(
        dll.fscanf,
        stream,
        _make_char_pointer(fmt),
        *args,
    )


def scanf(fmt: StringLike, *args: Format) -> int:
    return _base(dll.scanf, _make_char_pointer(fmt), *_make_format(*args))


def sscanf(string: StringLike, fmt: StringLike, *args: Format) -> int:
    return _base(
        dll.sscanf,
        _make_char_pointer(string),
        _make_char_pointer(fmt),
        *args,
    )


def fgetc(stream: PointerLike) -> int:
    return _base(dll.fgetc, stream)


def fgets(string: StringLike, n: int, stream: PointerLike) -> str:
    return _base(
        dll.fgets,
        _make_char_pointer(string),
        n,
        stream,
    )


def fputc(char: int, stream: PointerLike) -> int:
    return _base(dll.fputc, char, stream)


def fputs(string: StringLike, stream: PointerLike) -> int:
    return _base(dll.fputs, _make_char_pointer(string), stream)


def getc(stream: PointerLike) -> int:
    return _base(dll.getc, stream)


def getchar() -> int:
    return _base(dll.getchar)


def gets(string: StringLike) -> str:
    return _base(dll.gets, _make_char_pointer(string))


def putc(char: int, stream: PointerLike) -> int:
    return _base(dll.putc, char, stream)


def putchar(char: int) -> int:
    return _base(dll.putchar, char)


def puts(string: StringLike) -> int:
    return _base(dll.puts, _make_char_pointer(string))


def ungetc(char: int, stream: PointerLike) -> int:
    return _base(dll.ungetc, char, stream)


def perror(string: StringLike) -> None:
    return _base(dll.perror, _make_char_pointer(string))


def strtod(string: StringLike, endptr: TypedCPointer[str]) -> int:
    return _base(dll.strtod, _make_char_pointer(string), endptr)


def strtol(
    string: StringLike,
    endptr: TypedCPointer[str],
    base: int,
) -> int:
    return _base(
        dll.strtol,
        _make_char_pointer(string),
        endptr,
        base,
    )


def strtoul(
    string: StringLike,
    endptr: TypedCPointer[str],
    base: int,
) -> int:
    return _base(
        dll.strtoul,
        _make_char_pointer(string),
        endptr,
        base,
    )


def abort() -> None:
    return _base(dll.abort)


def exit(status: int) -> None:
    return _base(dll.exit, status)


def getenv(name: StringLike) -> str:
    return _base(dll.getenv, _make_char_pointer(name))


def system(string: StringLike) -> int:
    return _base(dll.system, _make_char_pointer(string))


def abs(x: int) -> int:
    return _base(dll.abs, x)


def labs(x: int) -> int:
    return _base(dll.labs, x)


def rand() -> int:
    return _base(dll.rand)


def srand(seed: int) -> None:
    return _base(dll.srand, seed)


def mblen(string: StringLike, n: int) -> int:
    return _base(
        dll.mblen,
        _make_char_pointer(string),
        n,
    )


def mbstowcs(pwcs: StringLike, string: StringLike, n: int) -> int:
    return _base(
        dll.mbstowcs,
        pwcs,
        _make_char_pointer(string),
        n,
    )


def mbtowc(pwc: StringLike, string: StringLike, n: int) -> int:
    return _base(
        dll.mbtowc,
        pwc,
        _make_char_pointer(string),
        n,
    )


def wcstombs(string: StringLike, pwcs: str, n: int) -> int:
    return _base(dll.wcstombs, _make_char_pointer(string), pwcs, n)


def wctomb(string: StringLike, wchar: str) -> int:
    return _base(dll.wctomb, _make_char_pointer(string), wchar)


def memchr(string: TypedCPointer[Any], c: int, n: int) -> VoidPointer:
    return _base(dll.memchr, string, c, n)


def memcmp(
    str1: TypedCPointer[Any],
    str2: TypedCPointer[Any],
    n: int,
) -> int:
    return _base(dll.memcmp, str1, str2, n)


def memcpy(
    dest: TypedCPointer[Any],
    src: TypedCPointer[Any],
    n: int,
) -> VoidPointer:
    return _base(dll.memcpy, dest, src, n)


def memmove(
    dest: TypedCPointer[Any],
    src: TypedCPointer[Any],
    n: int,
) -> VoidPointer:
    return _base(dll.memmove, dest, src, n)


def memset(string: TypedCPointer[Any], c: int, n: int) -> VoidPointer:
    return _base(dll.memset, string, c, n)


def strcat(dest: StringLike, src: StringLike) -> str:
    return _base(
        dll.strcat,
        _make_char_pointer(dest),
        _make_char_pointer(src),
    )


def strncat(dest: StringLike, src: StringLike, n: int) -> str:
    return _base(
        dll.strncat,
        _make_char_pointer(dest),
        _make_char_pointer(src),
        n,
    )


def strchr(string: StringLike, c: int) -> str:
    return _base(dll.strchr, _make_char_pointer(string), c)


def strcmp(str1: StringLike, str2: StringLike) -> int:
    return _base(
        dll.strcmp,
        _make_char_pointer(str1),
        _make_char_pointer(str2),
    )


def strncmp(str1: StringLike, str2: StringLike, n: int) -> int:
    return _base(
        dll.strncmp,
        _make_char_pointer(str1),
        _make_char_pointer(str2),
        n,
    )


def strcoll(str1: StringLike, str2: StringLike) -> int:
    return _base(
        dll.strcoll,
        _make_char_pointer(str1),
        _make_char_pointer(str2),
    )


def strcpy(dest: StringLike, src: StringLike) -> str:
    return _base(
        dll.strcpy,
        _make_char_pointer(dest),
        _make_char_pointer(src),
    )


def strncpy(dest: StringLike, src: StringLike, n: int) -> str:
    return _base(
        dll.strncpy,
        _make_char_pointer(dest),
        _make_char_pointer(src),
        n,
    )


def strcspn(str1: StringLike, str2: StringLike) -> int:
    return _base(
        dll.strcspn,
        _make_char_pointer(str1),
        _make_char_pointer(str2),
    )


def strerror(errnum: int) -> str:
    return _base(dll.strerror, errnum)


def strlen(string: StringLike) -> int:
    return _base(dll.strlen, _make_char_pointer(string))


def strpbrk(str1: StringLike, str2: StringLike) -> str:
    return _base(
        dll.strpbrk,
        _make_char_pointer(str1),
        _make_char_pointer(str2),
    )


def strrchr(string: StringLike, c: int) -> str:
    return _base(dll.strrchr, _make_char_pointer(string), c)


def strspn(str1: StringLike, str2: StringLike) -> int:
    return _base(
        dll.strspn,
        _make_char_pointer(str1),
        _make_char_pointer(str2),
    )


def strstr(haystack: StringLike, needle: StringLike) -> str:
    return _base(
        dll.strstr,
        _make_char_pointer(haystack),
        _make_char_pointer(needle),
    )


def strtok(string: StringLike, delim: StringLike) -> str:
    return _base(
        dll.strtok,
        _make_char_pointer(string),
        _make_char_pointer(delim),
    )


def strxfrm(dest: StringLike, src: StringLike, n: int) -> int:
    return _base(
        dll.strxfrm,
        _make_char_pointer(dest),
        _make_char_pointer(src),
        n,
    )


def asctime(timeptr: StructPointer[Tm]) -> str:
    return _base(dll.asctime, timeptr)


def clock() -> int:
    return _base(dll.clock)


def ctime(timer: TypedCPointer[int]) -> str:
    return _base(dll.ctime, timer)


def difftime(time1: int, time2: int) -> int:
    return _base(dll.difftime, time1, time2)


def mktime(timeptr: StructPointer[Tm]) -> int:
    return _base(dll.mktime, timeptr)


def strftime(
    string: StringLike,
    maxsize: int,
    fmt: StringLike,
    timeptr: StructPointer[Tm],
) -> int:
    return _base(
        dll.strftime,
        _make_char_pointer(string),
        maxsize,
        _make_char_pointer(fmt),
        timeptr,
    )


def time(timer: TypedCPointer[int]) -> int:
    return _base(dll.time, timer)


def div(numer: int, denom: int) -> DivT:
    return _base(dll.div, numer, denom)


def ldiv(numer: int, denom: int) -> LDivT:
    return _base(dll.ldiv, numer, denom)


def localeconv() -> StructPointer[Lconv]:
    return _base(dll.localeconv)


def c_raise(sig: int) -> int:
    return _base(ct_raise, sig)


def c_malloc(size: int) -> VoidPointer:
    return _base(_malloc, size)


def c_calloc(items: int, size: int) -> VoidPointer:
    return _base(_calloc, items, size)


def c_realloc(ptr: PointerLike, size: int) -> VoidPointer:
    return _base(_realloc, ptr, size)


def c_free(ptr: PointerLike) -> None:
    return _base(_free, ptr)


def gmtime(timer: PointerLike) -> StructPointer[Tm]:
    return _base(dll.gmtime, timer)
