import ctypes
import inspect
import warnings
from types import FunctionType
from typing import (
    TYPE_CHECKING, Any, Callable, Dict, Iterable, Iterator, Optional, Sequence,
    Type, TypeVar, Union
)

from _pointers import add_ref

from ._cstd import c_calloc as _calloc
from ._cstd import c_free as _free
from ._cstd import c_malloc as _malloc
from ._cstd import c_raise as ct_raise
from ._cstd import c_realloc as _realloc
from ._cstd import dll
from ._utils import get_mapped, get_py
from .base_pointers import BaseCPointer, BasePointer
from .c_pointer import TypedCPointer, VoidPointer
from .exceptions import InvalidBindingParameter
from .std_structs import STRUCT_MAP, DivT, Lconv, LDivT, Tm
from .structure import StructPointer
from .util import NULL, Nullable, handle

if TYPE_CHECKING:
    from .structure import Struct

T = TypeVar("T")

PointerLike = Nullable[Optional[Union[TypedCPointer[T], VoidPointer]]]
StringLike = Optional[Union[str, bytes, VoidPointer, TypedCPointer[bytes]]]
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
        struct_type = struct_map.get(res_typ._type_)  # type: ignore

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
            else StructPointer(id(struct), struct)
        )
    # type safety gets mad if i dont use elif here
    elif current is ctypes.c_void_p:
        res = VoidPointer(res, ctypes.sizeof(ctypes.c_void_p(res)))

    elif issubclass(res_typ, ctypes.Structure):
        st = struct_map.get(res_typ)
        if st:
            res = st.from_existing(res)

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
    struct_map: StructMap,
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
                struct_map,
            )
            continue
        is_c_func: bool = isinstance(
            typ,
            PyCFuncPtrType,
        )
        n_type = get_py(typ) if not is_c_func else FunctionType

        if typ.__name__.startswith("LP_"):
            ptr_tp = typ._type_  # type: ignore
            if issubclass(ptr_tp, ctypes.Structure):  # type: ignore
                n_type = StructPointer
                struct = struct_map.get(ptr_tp)

                if not struct:
                    warnings.warn(
                        f"struct {ptr_tp.__name__} not in struct map",
                        UserWarning,
                    )

        is_type: bool = isinstance(value, type)

        if n_type is Any:
            continue

        if not (isinstance if not is_type else issubclass)(value, n_type):
            v_type = type(value) if not is_type else value

            if (n_type in {
                BasePointer,
                BaseCPointer,
                StructPointer
            }) and (value is None):
                continue

            if (n_type is FunctionType) and is_c_func:
                continue

            if (
                typ
                in {
                    ctypes.c_char_p,
                    ctypes.c_void_p,
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
    struct_map: StructMap,
) -> None:
    if not fn.argtypes:
        return

    _process_args(args, fn.argtypes, fn.__name__, struct_map)


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


@handle
def binding_base(
    fn: "ctypes._NamedFuncPointer",
    *simple_args,
    map_extra: Optional[StructMap] = None,
) -> Any:
    smap = {**STRUCT_MAP, **(map_extra or {})}

    args = [i if i is not NULL else None for i in simple_args]

    validator_args = [
        arg
        if (
            (not isinstance(arg, FunctionType))
            and (not isinstance(arg, PyCFuncPtrType))
        )
        else _solve_func(
            arg,  # type: ignore
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
        smap,
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


def make_string(data: StringLike) -> Union[bytes, ctypes.c_char_p]:
    if (type(data) not in {VoidPointer, str, bytes, TypedCPointer}) and data:
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

    if not data:
        data = ctypes.c_char_p(None)  # type: ignore

    assert isinstance(data, ctypes.c_char_p), f"{data} is not a char*"
    return data


def make_format(*args: Format) -> Iterator[Format]:
    for i in args:
        if isinstance(i, (VoidPointer, str, bytes)):
            yield make_string(i)  # type: ignore
            continue

        yield i


def make_char(char: CharLike) -> bytes:
    if isinstance(char, int):
        return chr(char).encode()

    charp = make_string(char)
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
    return binding_base(dll.isalnum, make_char(c))


def isalpha(c: CharLike) -> int:
    return binding_base(dll.isalpha, make_char(c))


def iscntrl(c: CharLike) -> int:
    return binding_base(dll.iscntrl, make_char(c))


def isdigit(c: CharLike) -> int:
    return binding_base(dll.isdigit, make_char(c))


def isgraph(c: CharLike) -> int:
    return binding_base(dll.isgraph, make_char(c))


def islower(c: CharLike) -> int:
    return binding_base(dll.islower, make_char(c))


def isprint(c: CharLike) -> int:
    return binding_base(dll.isprint, make_char(c))


def ispunct(c: CharLike) -> int:
    return binding_base(dll.ispunct, make_char(c))


def isspace(c: CharLike) -> int:
    return binding_base(dll.isspace, make_char(c))


def isupper(c: CharLike) -> int:
    return binding_base(dll.isupper, make_char(c))


def isxdigit(c: CharLike) -> int:
    return binding_base(dll.isxdigit, make_char(c))


def tolower(c: CharLike) -> str:
    return binding_base(dll.tolower, make_char(c))


def toupper(c: CharLike) -> str:
    return binding_base(dll.toupper, make_char(c))


def setlocale(category: int, locale: StringLike) -> str:
    return binding_base(dll.setlocale, category, make_string(locale))


def frexp(x: float, exponent: TypedPtr[int]) -> int:
    return binding_base(dll.frexp, x, exponent)


def ldexp(x: float, exponent: int) -> int:
    return binding_base(dll.ldexp, x, exponent)


def modf(x: float, integer: TypedPtr[float]) -> int:
    return binding_base(dll.modf, x, integer)


def fclose(stream: PointerLike) -> int:
    return binding_base(dll.fclose, stream)


def clearerr(stream: PointerLike) -> None:
    return binding_base(dll.clearerr, stream)


def feof(stream: PointerLike) -> int:
    return binding_base(dll.feof, stream)


def ferror(stream: PointerLike) -> int:
    return binding_base(dll.ferror, stream)


def fflush(stream: PointerLike) -> int:
    return binding_base(dll.fflush, stream)


def fgetpos(stream: PointerLike, pos: PointerLike) -> int:
    return binding_base(dll.fgetpos, stream, pos)


def fopen(filename: StringLike, mode: StringLike) -> VoidPointer:
    return binding_base(
        dll.fopen,
        make_string(filename),
        make_string(mode),
    )


def fread(
    ptr: PointerLike,
    size: int,
    nmemb: int,
    stream: PointerLike,
) -> int:
    return binding_base(dll.fread, ptr, size, nmemb, stream)


def freopen(
    filename: StringLike,
    mode: StringLike,
    stream: PointerLike,
) -> VoidPointer:
    return binding_base(
        dll.freopen,
        make_string(filename),
        make_string(mode),
        stream,
    )


def fseek(stream: PointerLike, offset: int, whence: int) -> int:
    return binding_base(dll.fseek, stream, offset, whence)


def fsetpos(stream: PointerLike, pos: PointerLike) -> int:
    return binding_base(dll.fsetpos, stream, pos)


def ftell(stream: PointerLike) -> int:
    return binding_base(dll.ftell, stream)


def fwrite(
    ptr: PointerLike,
    size: int,
    nmemb: int,
    stream: PointerLike,
) -> int:
    return binding_base(dll.fwrite, ptr, size, nmemb, stream)


def remove(filename: StringLike) -> int:
    return binding_base(dll.remove, make_string(filename))


def rename(old_filename: StringLike, new_filename: StringLike) -> int:
    return binding_base(
        dll.rename,
        make_string(old_filename),
        make_string(new_filename),
    )


def rewind(stream: PointerLike) -> None:
    return binding_base(dll.rewind, stream)


def setbuf(stream: PointerLike, buffer: StringLike) -> None:
    return binding_base(dll.setbuf, stream, make_string(buffer))


def setvbuf(
    stream: PointerLike,
    buffer: str,
    mode: int,
    size: int,
) -> int:
    return binding_base(
        dll.setvbuf,
        stream,
        make_string(buffer),
        mode,
        size,
    )


def tmpfile() -> VoidPointer:
    return binding_base(dll.tmpfile)


def tmpnam(string: str) -> str:
    return binding_base(dll.tmpnam, make_string(string))


def fprintf(stream: PointerLike, fmt: StringLike, *args: Format) -> int:
    return binding_base(
        dll.fprintf,
        stream,
        make_string(fmt),
        *make_format(*args),
    )


def printf(fmt: StringLike, *args: Format) -> int:
    return binding_base(dll.printf, make_string(fmt), *make_format(*args))


def sprintf(string: StringLike, fmt: StringLike, *args: Format) -> int:
    return binding_base(
        dll.sprintf,
        make_string(string),
        make_string(fmt),
        *make_format(*args),
    )


def fscanf(stream: PointerLike, fmt: StringLike, *args: Format) -> int:
    return binding_base(
        dll.fscanf,
        stream,
        make_string(fmt),
        *make_format(*args),
    )


def scanf(fmt: StringLike, *args: Format) -> int:
    return binding_base(dll.scanf, make_string(fmt), *make_format(*args))


def sscanf(string: StringLike, fmt: StringLike, *args: Format) -> int:
    return binding_base(
        dll.sscanf,
        make_string(string),
        make_string(fmt),
        *make_format(*args),
    )


def fgetc(stream: PointerLike) -> int:
    return binding_base(dll.fgetc, stream)


def fgets(string: StringLike, n: int, stream: PointerLike) -> str:
    return binding_base(
        dll.fgets,
        make_string(string),
        n,
        stream,
    )


def fputc(char: int, stream: PointerLike) -> int:
    return binding_base(dll.fputc, char, stream)


def fputs(string: StringLike, stream: PointerLike) -> int:
    return binding_base(dll.fputs, make_string(string), stream)


def getc(stream: PointerLike) -> int:
    return binding_base(dll.getc, stream)


def getchar() -> int:
    return binding_base(dll.getchar)


def gets(string: StringLike) -> str:
    return binding_base(dll.gets, make_string(string))


def putc(char: int, stream: PointerLike) -> int:
    return binding_base(dll.putc, char, stream)


def putchar(char: int) -> int:
    return binding_base(dll.putchar, char)


def puts(string: StringLike) -> int:
    return binding_base(dll.puts, make_string(string))


def ungetc(char: int, stream: PointerLike) -> int:
    return binding_base(dll.ungetc, char, stream)


def perror(string: StringLike) -> None:
    return binding_base(dll.perror, make_string(string))


def strtod(string: StringLike, endptr: PointerLike) -> int:
    return binding_base(dll.strtod, make_string(string), endptr)


def strtol(
    string: StringLike,
    endptr: PointerLike,
    base: int,
) -> int:
    return binding_base(
        dll.strtol,
        make_string(string),
        endptr,
        base,
    )


def strtoul(
    string: StringLike,
    endptr: PointerLike,
    base: int,
) -> int:
    return binding_base(
        dll.strtoul,
        make_string(string),
        endptr,
        base,
    )


def abort() -> None:
    return binding_base(dll.abort)


def exit(status: int) -> None:
    return binding_base(dll.exit, status)


def getenv(name: StringLike) -> str:
    return binding_base(dll.getenv, make_string(name))


def system(string: StringLike) -> int:
    return binding_base(dll.system, make_string(string))


def abs(x: int) -> int:
    return binding_base(dll.abs, x)


def labs(x: int) -> int:
    return binding_base(dll.labs, x)


def rand() -> int:
    return binding_base(dll.rand)


def srand(seed: int) -> None:
    return binding_base(dll.srand, seed)


def mblen(string: StringLike, n: int) -> int:
    return binding_base(
        dll.mblen,
        make_string(string),
        n,
    )


def mbstowcs(pwcs: StringLike, string: StringLike, n: int) -> int:
    return binding_base(
        dll.mbstowcs,
        pwcs,
        make_string(string),
        n,
    )


def mbtowc(pwc: StringLike, string: StringLike, n: int) -> int:
    return binding_base(
        dll.mbtowc,
        pwc,
        make_string(string),
        n,
    )


def wcstombs(string: StringLike, pwcs: str, n: int) -> int:
    return binding_base(dll.wcstombs, make_string(string), pwcs, n)


def wctomb(string: StringLike, wchar: str) -> int:
    return binding_base(dll.wctomb, make_string(string), wchar)


def memchr(string: PointerLike, c: int, n: int) -> VoidPointer:
    return binding_base(dll.memchr, string, c, n)


def memcmp(
    str1: PointerLike,
    str2: PointerLike,
    n: int,
) -> int:
    return binding_base(dll.memcmp, str1, str2, n)


def memcpy(
    dest: PointerLike,
    src: PointerLike,
    n: int,
) -> VoidPointer:
    return binding_base(dll.memcpy, dest, src, n)


def memmove(
    dest: PointerLike,
    src: PointerLike,
    n: int,
) -> VoidPointer:
    return binding_base(dll.memmove, dest, src, n)


def memset(string: PointerLike, c: int, n: int) -> VoidPointer:
    return binding_base(dll.memset, string, c, n)


def strcat(dest: StringLike, src: StringLike) -> str:
    return binding_base(
        dll.strcat,
        make_string(dest),
        make_string(src),
    )


def strncat(dest: StringLike, src: StringLike, n: int) -> str:
    return binding_base(
        dll.strncat,
        make_string(dest),
        make_string(src),
        n,
    )


def strchr(string: StringLike, c: int) -> str:
    return binding_base(dll.strchr, make_string(string), c)


def strcmp(str1: StringLike, str2: StringLike) -> int:
    return binding_base(
        dll.strcmp,
        make_string(str1),
        make_string(str2),
    )


def strncmp(str1: StringLike, str2: StringLike, n: int) -> int:
    return binding_base(
        dll.strncmp,
        make_string(str1),
        make_string(str2),
        n,
    )


def strcoll(str1: StringLike, str2: StringLike) -> int:
    return binding_base(
        dll.strcoll,
        make_string(str1),
        make_string(str2),
    )


def strcpy(dest: StringLike, src: StringLike) -> str:
    return binding_base(
        dll.strcpy,
        make_string(dest),
        make_string(src),
    )


def strncpy(dest: StringLike, src: StringLike, n: int) -> str:
    return binding_base(
        dll.strncpy,
        make_string(dest),
        make_string(src),
        n,
    )


def strcspn(str1: StringLike, str2: StringLike) -> int:
    return binding_base(
        dll.strcspn,
        make_string(str1),
        make_string(str2),
    )


def strerror(errnum: int) -> str:
    return binding_base(dll.strerror, errnum)


def strlen(string: StringLike) -> int:
    return binding_base(dll.strlen, make_string(string))


def strpbrk(str1: StringLike, str2: StringLike) -> str:
    return binding_base(
        dll.strpbrk,
        make_string(str1),
        make_string(str2),
    )


def strrchr(string: StringLike, c: int) -> str:
    return binding_base(dll.strrchr, make_string(string), c)


def strspn(str1: StringLike, str2: StringLike) -> int:
    return binding_base(
        dll.strspn,
        make_string(str1),
        make_string(str2),
    )


def strstr(haystack: StringLike, needle: StringLike) -> str:
    return binding_base(
        dll.strstr,
        make_string(haystack),
        make_string(needle),
    )


def strtok(string: StringLike, delim: StringLike) -> str:
    return binding_base(
        dll.strtok,
        make_string(string),
        make_string(delim),
    )


def strxfrm(dest: StringLike, src: StringLike, n: int) -> int:
    return binding_base(
        dll.strxfrm,
        make_string(dest),
        make_string(src),
        n,
    )


def asctime(timeptr: StructPointer[Tm]) -> str:
    return binding_base(dll.asctime, timeptr)


def clock() -> int:
    return binding_base(dll.clock)


def ctime(timer: TypedPtr[int]) -> str:
    return binding_base(dll.ctime, timer)


def difftime(time1: int, time2: int) -> int:
    return binding_base(dll.difftime, time1, time2)


def mktime(timeptr: StructPointer[Tm]) -> int:
    return binding_base(dll.mktime, timeptr)


def strftime(
    string: StringLike,
    maxsize: int,
    fmt: StringLike,
    timeptr: StructPointer[Tm],
) -> int:
    return binding_base(
        dll.strftime,
        make_string(string),
        maxsize,
        make_string(fmt),
        timeptr,
    )


def time(timer: TypedPtr[int]) -> int:
    return binding_base(dll.time, timer)


def div(numer: int, denom: int) -> DivT:
    return binding_base(dll.div, numer, denom)


def ldiv(numer: int, denom: int) -> LDivT:
    return binding_base(dll.ldiv, numer, denom)


def localeconv() -> StructPointer[Lconv]:
    return binding_base(dll.localeconv)


def c_raise(sig: int) -> int:
    return binding_base(ct_raise, sig)


def c_malloc(size: int) -> VoidPointer:
    return binding_base(_malloc, size)


def c_calloc(items: int, size: int) -> VoidPointer:
    return binding_base(_calloc, items, size)


def c_realloc(ptr: PointerLike, size: int) -> VoidPointer:
    return binding_base(_realloc, ptr, size)


def c_free(ptr: PointerLike) -> None:
    return binding_base(_free, ptr)


def gmtime(timer: PointerLike) -> StructPointer[Tm]:
    return binding_base(dll.gmtime, timer)


def signal(signum: int, func: Callable[[int], Any]) -> None:
    return binding_base(dll.signal, signum, func)


def qsort(
    base: PointerLike,
    nitem: int,
    size: int,
    compar: Callable[
        [Any, Any],
        int,
    ],
) -> None:
    return binding_base(dll.qsort, base, nitem, size, compar)


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
    return binding_base(dll.bsearch, key, base, nitems, size, compar)


def sizeof(obj: Any) -> int:
    try:
        return ctypes.sizeof(obj)
    except TypeError:
        return ctypes.sizeof(get_mapped(obj))
