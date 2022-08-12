import ctypes
import inspect
from types import FunctionType
from typing import (
    TYPE_CHECKING, Any, Callable, Dict, Iterable, Iterator, Optional, Sequence,
    Type, TypeVar, Union
)

from _pointers import add_ref

from . import _cstd
from ._cstd import STRUCT_MAP, DivT, Lconv, LDivT, Tm
from ._cstd import c_calloc as _calloc
from ._cstd import c_free as _free
from ._cstd import c_malloc as _malloc
from ._cstd import c_raise as ct_raise
from ._cstd import c_realloc as _realloc
from ._cstd import dll
from .base_pointers import BaseCPointer, BasePointer
from .c_pointer import TypedCPointer, VoidPointer
from .c_utils import get_mapped, get_py
from .exceptions import InvalidBindingParameter
from .struct import StructPointer

if TYPE_CHECKING:
    from .struct import Struct

T = TypeVar("T")

PointerLike = Union[TypedCPointer[T], VoidPointer, None]
StringLike = Union[str, bytes, VoidPointer, TypedCPointer[bytes]]
Format = Union[StringLike, PointerLike]
TypedPtr = Optional[PointerLike[T]]
PyCFuncPtrType = type(ctypes.CFUNCTYPE(None))

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
    "signal",
    "qsort",
    "bsearch",
    "sizeof",
    "PointerLike",
    "StringLike",
    "Format",
    "TypedPtr",
)


def _not_null(data: Optional[T]) -> T:
    assert data is not None, f"{data} is None"
    return data


StructMap = Dict[Type[ctypes.Structure], Type["Struct"]]
CharLike = Union[StringLike, int]


class _CFuncTransport:
    def __init__(
        self,
        c_func: "ctypes._FuncPointer",
        py_func: Callable,
    ) -> None:
        add_ref(c_func)
        self._c_func = c_func
        self._py_func = py_func

    @property
    def c_func(self) -> "ctypes._FuncPointer":
        return self._c_func

    @property
    def py_func(self) -> Callable:
        return self._py_func


def _decode_type(
    res: Any,
    struct_map: StructMap,
    current: Optional[Type["ctypes._CData"]],
) -> Any:
    res_typ = type(res)

    if res_typ.__name__.startswith("LP_"):
        struct_type = struct_map.get(getattr(_cstd, res_typ.__name__[3:]))
        struct = (
            struct_type.from_existing(res.contents) if struct_type else None
        )  # fmt: off

        res = (
            TypedCPointer(
                ctypes.addressof(res),
                res_typ,
                ctypes.sizeof(res),
                alt=True,
            )
            if not issubclass(type(res.contents), ctypes.Structure)
            else StructPointer(id(struct), type(_not_null(struct)), struct)
        )
    # type safety gets mad if i dont use elif here
    elif current is ctypes.c_void_p:
        res = VoidPointer(res, ctypes.sizeof(ctypes.c_void_p(res)))

    elif issubclass(res_typ, ctypes.Structure):
        struct = struct_map.get(res_typ)
        if struct:
            res = struct.from_existing(res)

    elif isinstance(res, bytes):
        return res.decode()

    return res


def _decode_response(
    res: Any,
    struct_map: StructMap,
    fn: "ctypes._NamedFuncPointer",
) -> Any:
    return _decode_type(res, struct_map, fn.restype)  # type: ignore


def _process_args(
    args: Iterable[Any],
    argtypes: Sequence[Type["ctypes._CData"]],
    name: str,
) -> None:
    for index, (value, typ) in enumerate(zip(args, argtypes)):
        if value is inspect._empty:
            continue

        if isinstance(value, _CFuncTransport):
            py_func = value.py_func
            sig = inspect.signature(py_func)
            _process_args(
                [param.annotation for param in sig.parameters.values()],
                value.c_func._argtypes_,  # type: ignore
                py_func.__name__,
            )
            continue
        is_c_func: bool = isinstance(
            typ,
            PyCFuncPtrType,
        )
        n_type = get_py(typ) if not is_c_func else FunctionType

        is_type: bool = isinstance(value, type)

        if not (isinstance if not is_type else issubclass)(value, n_type):
            v_type = type(value) if not is_type else value

            if (n_type is BasePointer) and (value is None):
                continue

            if (n_type is FunctionType) and is_c_func:
                continue

            if (
                typ
                in {
                    ctypes.c_char_p,
                    ctypes.c_void_p,
                    ctypes.POINTER,
                }
            ) and (value is None):
                continue

            if ((v_type is ctypes.c_char_p) and (n_type is bytes)) or (
                issubclass(v_type, BaseCPointer) and (typ is ctypes.c_void_p)
            ):
                continue

            raise InvalidBindingParameter(
                f"argument {index + 1} of {name} got invalid type: expected {n_type.__name__}, got {v_type.__name__}"  # noqa
            )


def _validate_args(
    args: Iterable[Any],
    fn: "ctypes._NamedFuncPointer",
) -> None:
    if not fn.argtypes:
        return

    _process_args(args, fn.argtypes, fn.__name__)


def _solve_func(
    fn: Callable,
    ct_fn: "ctypes._FuncPointer",
    struct_map: StructMap,
) -> _CFuncTransport:
    at = ct_fn._argtypes_  # type: ignore

    @ctypes.CFUNCTYPE(ct_fn._restype_, *at)  # type: ignore
    def wrapper(*args):
        callback_args = []

        for value, ctype in zip(args, at):
            callback_args.append(_decode_type(value, struct_map, ctype))

        return fn(*callback_args)

    return _CFuncTransport(wrapper, fn)


def _base(
    fn: "ctypes._NamedFuncPointer",
    *args,
    map_extra: Optional[StructMap] = None,
) -> Any:
    smap = {**STRUCT_MAP, **(map_extra or {})}

    validator_args = [
        arg
        if ((not callable(arg)) and (not isinstance(arg, PyCFuncPtrType)))
        else _solve_func(
            arg,
            typ,  # type: ignore
            smap,
        )
        for arg, typ in zip(
            args,
            fn.argtypes or [None for _ in args],  # type: ignore
        )
    ]

    _validate_args(
        validator_args,
        fn,
    )

    res = fn(
        *[
            i
            if not isinstance(
                i,
                _CFuncTransport,
            )
            else i.c_func
            for i in validator_args
        ]
    )

    return _decode_response(
        res,
        smap,
        fn,
    )


def _make_string(data: StringLike) -> Union[bytes, ctypes.c_char_p]:
    if type(data) not in {VoidPointer, str, bytes, TypedCPointer}:
        raise InvalidBindingParameter(
            f"expected a string-like object, got {repr(data)}"  # noqa
        )

    if isinstance(data, bytes):
        return data

    is_typed_ptr: bool = isinstance(data, TypedCPointer)

    if isinstance(data, VoidPointer) or isinstance(data, TypedCPointer):
        # mypy is forcing me to call this twice
        if is_typed_ptr and (data.type is not bytes):  # type: ignore
            raise InvalidBindingParameter(
                f"{data} does not point to bytes",
            )

        if is_typed_ptr and (not data.alt):  # type: ignore
            return ctypes.c_char_p.from_address(data.ensure())
        return ctypes.c_char_p(data.ensure())

    if isinstance(data, str):
        return data.encode()

    assert isinstance(data, ctypes.c_char_p), f"{data} is not a char*"
    return data


def _make_format(*args: Format) -> Iterator[Format]:
    for i in args:
        if isinstance(i, (VoidPointer, str, bytes)):
            yield _make_string(i)  # type: ignore
            continue

        yield i


def _make_char(char: CharLike) -> bytes:
    if isinstance(char, int):
        return chr(char).encode()

    charp = _make_string(char)
    string = (
        charp
        if not isinstance(
            charp,
            ctypes.c_char_p,
        )
        else _not_null(charp.value)
    )

    if len(string) != 1:
        raise InvalidBindingParameter(
            f'"{string.decode()}" should have a length of 1',
        )

    return string


def isalnum(c: CharLike) -> int:
    return _base(dll.isalnum, _make_char(c))


def isalpha(c: CharLike) -> int:
    return _base(dll.isalpha, _make_char(c))


def iscntrl(c: CharLike) -> int:
    return _base(dll.iscntrl, _make_char(c))


def isdigit(c: CharLike) -> int:
    return _base(dll.isdigit, _make_char(c))


def isgraph(c: CharLike) -> int:
    return _base(dll.isgraph, _make_char(c))


def islower(c: CharLike) -> int:
    return _base(dll.islower, _make_char(c))


def isprint(c: CharLike) -> int:
    return _base(dll.isprint, _make_char(c))


def ispunct(c: CharLike) -> int:
    return _base(dll.ispunct, _make_char(c))


def isspace(c: CharLike) -> int:
    return _base(dll.isspace, _make_char(c))


def isupper(c: CharLike) -> int:
    return _base(dll.isupper, _make_char(c))


def isxdigit(c: CharLike) -> int:
    return _base(dll.isxdigit, _make_char(c))


def tolower(c: CharLike) -> str:
    return _base(dll.tolower, _make_char(c))


def toupper(c: CharLike) -> str:
    return _base(dll.toupper, _make_char(c))


def setlocale(category: int, locale: StringLike) -> str:
    return _base(dll.setlocale, category, _make_string(locale))


def frexp(x: float, exponent: TypedPtr[int]) -> int:
    return _base(dll.frexp, x, exponent)


def ldexp(x: float, exponent: int) -> int:
    return _base(dll.ldexp, x, exponent)


def modf(x: float, integer: TypedPtr[float]) -> int:
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
        _make_string(filename),
        _make_string(mode),
    )


def fread(
    ptr: PointerLike,
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
        _make_string(filename),
        _make_string(mode),
        stream,
    )


def fseek(stream: PointerLike, offset: int, whence: int) -> int:
    return _base(dll.fseek, stream, offset, whence)


def fsetpos(stream: PointerLike, pos: PointerLike) -> int:
    return _base(dll.fsetpos, stream, pos)


def ftell(stream: PointerLike) -> int:
    return _base(dll.ftell, stream)


def fwrite(
    ptr: PointerLike,
    size: int,
    nmemb: int,
    stream: PointerLike,
) -> int:
    return _base(dll.fwrite, ptr, size, nmemb, stream)


def remove(filename: StringLike) -> int:
    return _base(dll.remove, _make_string(filename))


def rename(old_filename: StringLike, new_filename: StringLike) -> int:
    return _base(
        dll.rename,
        _make_string(old_filename),
        _make_string(new_filename),
    )


def rewind(stream: PointerLike) -> None:
    return _base(dll.rewind, stream)


def setbuf(stream: PointerLike, buffer: StringLike) -> None:
    return _base(dll.setbuf, stream, _make_string(buffer))


def setvbuf(
    stream: PointerLike,
    buffer: str,
    mode: int,
    size: int,
) -> int:
    return _base(
        dll.setvbuf,
        stream,
        _make_string(buffer),
        mode,
        size,
    )


def tmpfile() -> VoidPointer:
    return _base(dll.tmpfile)


def tmpnam(string: str) -> str:
    return _base(dll.tmpnam, _make_string(string))


def fprintf(stream: PointerLike, fmt: StringLike, *args: Format) -> int:
    return _base(
        dll.fprintf,
        stream,
        _make_string(fmt),
        *_make_format(*args),
    )


def printf(fmt: StringLike, *args: Format) -> int:
    return _base(dll.printf, _make_string(fmt), *_make_format(*args))


def sprintf(string: StringLike, fmt: StringLike, *args: Format) -> int:
    return _base(
        dll.sprintf,
        _make_string(string),
        _make_string(fmt),
        *_make_format(*args),
    )


def fscanf(stream: PointerLike, fmt: StringLike, *args: Format) -> int:
    return _base(
        dll.fscanf,
        stream,
        _make_string(fmt),
        *_make_format(*args),
    )


def scanf(fmt: StringLike, *args: Format) -> int:
    return _base(dll.scanf, _make_string(fmt), *_make_format(*args))


def sscanf(string: StringLike, fmt: StringLike, *args: Format) -> int:
    return _base(
        dll.sscanf,
        _make_string(string),
        _make_string(fmt),
        *_make_format(*args),
    )


def fgetc(stream: PointerLike) -> int:
    return _base(dll.fgetc, stream)


def fgets(string: StringLike, n: int, stream: PointerLike) -> str:
    return _base(
        dll.fgets,
        _make_string(string),
        n,
        stream,
    )


def fputc(char: int, stream: PointerLike) -> int:
    return _base(dll.fputc, char, stream)


def fputs(string: StringLike, stream: PointerLike) -> int:
    return _base(dll.fputs, _make_string(string), stream)


def getc(stream: PointerLike) -> int:
    return _base(dll.getc, stream)


def getchar() -> int:
    return _base(dll.getchar)


def gets(string: StringLike) -> str:
    return _base(dll.gets, _make_string(string))


def putc(char: int, stream: PointerLike) -> int:
    return _base(dll.putc, char, stream)


def putchar(char: int) -> int:
    return _base(dll.putchar, char)


def puts(string: StringLike) -> int:
    return _base(dll.puts, _make_string(string))


def ungetc(char: int, stream: PointerLike) -> int:
    return _base(dll.ungetc, char, stream)


def perror(string: StringLike) -> None:
    return _base(dll.perror, _make_string(string))


def strtod(string: StringLike, endptr: PointerLike) -> int:
    return _base(dll.strtod, _make_string(string), endptr)


def strtol(
    string: StringLike,
    endptr: PointerLike,
    base: int,
) -> int:
    return _base(
        dll.strtol,
        _make_string(string),
        endptr,
        base,
    )


def strtoul(
    string: StringLike,
    endptr: PointerLike,
    base: int,
) -> int:
    return _base(
        dll.strtoul,
        _make_string(string),
        endptr,
        base,
    )


def abort() -> None:
    return _base(dll.abort)


def exit(status: int) -> None:
    return _base(dll.exit, status)


def getenv(name: StringLike) -> str:
    return _base(dll.getenv, _make_string(name))


def system(string: StringLike) -> int:
    return _base(dll.system, _make_string(string))


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
        _make_string(string),
        n,
    )


def mbstowcs(pwcs: StringLike, string: StringLike, n: int) -> int:
    return _base(
        dll.mbstowcs,
        pwcs,
        _make_string(string),
        n,
    )


def mbtowc(pwc: StringLike, string: StringLike, n: int) -> int:
    return _base(
        dll.mbtowc,
        pwc,
        _make_string(string),
        n,
    )


def wcstombs(string: StringLike, pwcs: str, n: int) -> int:
    return _base(dll.wcstombs, _make_string(string), pwcs, n)


def wctomb(string: StringLike, wchar: str) -> int:
    return _base(dll.wctomb, _make_string(string), wchar)


def memchr(string: PointerLike, c: int, n: int) -> VoidPointer:
    return _base(dll.memchr, string, c, n)


def memcmp(
    str1: PointerLike,
    str2: PointerLike,
    n: int,
) -> int:
    return _base(dll.memcmp, str1, str2, n)


def memcpy(
    dest: PointerLike,
    src: PointerLike,
    n: int,
) -> VoidPointer:
    return _base(dll.memcpy, dest, src, n)


def memmove(
    dest: PointerLike,
    src: PointerLike,
    n: int,
) -> VoidPointer:
    return _base(dll.memmove, dest, src, n)


def memset(string: PointerLike, c: int, n: int) -> VoidPointer:
    return _base(dll.memset, string, c, n)


def strcat(dest: StringLike, src: StringLike) -> str:
    return _base(
        dll.strcat,
        _make_string(dest),
        _make_string(src),
    )


def strncat(dest: StringLike, src: StringLike, n: int) -> str:
    return _base(
        dll.strncat,
        _make_string(dest),
        _make_string(src),
        n,
    )


def strchr(string: StringLike, c: int) -> str:
    return _base(dll.strchr, _make_string(string), c)


def strcmp(str1: StringLike, str2: StringLike) -> int:
    return _base(
        dll.strcmp,
        _make_string(str1),
        _make_string(str2),
    )


def strncmp(str1: StringLike, str2: StringLike, n: int) -> int:
    return _base(
        dll.strncmp,
        _make_string(str1),
        _make_string(str2),
        n,
    )


def strcoll(str1: StringLike, str2: StringLike) -> int:
    return _base(
        dll.strcoll,
        _make_string(str1),
        _make_string(str2),
    )


def strcpy(dest: StringLike, src: StringLike) -> str:
    return _base(
        dll.strcpy,
        _make_string(dest),
        _make_string(src),
    )


def strncpy(dest: StringLike, src: StringLike, n: int) -> str:
    return _base(
        dll.strncpy,
        _make_string(dest),
        _make_string(src),
        n,
    )


def strcspn(str1: StringLike, str2: StringLike) -> int:
    return _base(
        dll.strcspn,
        _make_string(str1),
        _make_string(str2),
    )


def strerror(errnum: int) -> str:
    return _base(dll.strerror, errnum)


def strlen(string: StringLike) -> int:
    return _base(dll.strlen, _make_string(string))


def strpbrk(str1: StringLike, str2: StringLike) -> str:
    return _base(
        dll.strpbrk,
        _make_string(str1),
        _make_string(str2),
    )


def strrchr(string: StringLike, c: int) -> str:
    return _base(dll.strrchr, _make_string(string), c)


def strspn(str1: StringLike, str2: StringLike) -> int:
    return _base(
        dll.strspn,
        _make_string(str1),
        _make_string(str2),
    )


def strstr(haystack: StringLike, needle: StringLike) -> str:
    return _base(
        dll.strstr,
        _make_string(haystack),
        _make_string(needle),
    )


def strtok(string: StringLike, delim: StringLike) -> str:
    return _base(
        dll.strtok,
        _make_string(string),
        _make_string(delim),
    )


def strxfrm(dest: StringLike, src: StringLike, n: int) -> int:
    return _base(
        dll.strxfrm,
        _make_string(dest),
        _make_string(src),
        n,
    )


def asctime(timeptr: StructPointer[Tm]) -> str:
    return _base(dll.asctime, timeptr)


def clock() -> int:
    return _base(dll.clock)


def ctime(timer: TypedPtr[int]) -> str:
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
        _make_string(string),
        maxsize,
        _make_string(fmt),
        timeptr,
    )


def time(timer: TypedPtr[int]) -> int:
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


def signal(signum: int, func: Callable[[int], Any]) -> None:
    return _base(dll.signal, signum, func)


def qsort(
    base: PointerLike,
    nitem: int,
    size: int,
    compar: Callable[
        [Any, Any],
        int,
    ],
) -> None:
    return _base(dll.qsort, base, nitem, size, compar)


def bsearch(
    key: PointerLike,
    base: PointerLike,
    nitems: int,
    size: int,
    compar: Callable[
        [Any, Any],
        int,
    ],
) -> VoidPointer:
    return _base(dll.bsearch, key, base, nitems, size, compar)


def sizeof(obj: Any) -> int:
    try:
        return ctypes.sizeof(obj)
    except TypeError:
        return ctypes.sizeof(get_mapped(obj))
