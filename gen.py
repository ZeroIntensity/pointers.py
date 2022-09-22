# this file shouldnt be pep 8 checked
from __future__ import annotations

import ctypes
import re

import requests
from bs4 import BeautifulSoup, Tag

PAGES: dict[str, BeautifulSoup] = {}
BASE_URL: str = "https://docs.python.org/3.11/c-api"
C_FUNC = re.compile(
    r"(((.+) )?(\w+(\**)*)) (\w+)\(((((.+ \w+(\[\])?,?)*(, ?\.\.\.)?))|void)\)"
)


def ct(data: str) -> str:
    return f"ctypes.{data}"


def ctc(data: str) -> str:
    return f"ctypes.c_{data}"


def ctp(data: str) -> str:
    return f"ctypes.POINTER({data})"


WCHAR_P = ctc("wchar_p")
CHAR_P = ctc("char_p")
VOID_P = ctc("void_p")
WCHAR = ctc("wchar")
DOUBLE_QUOTE: str = '"'
TRIPLE_QUOTE: str = '"""'

C_TYPES = {
    "void": "None",
    "PyObject*": ct("py_object"),
    "int": ctc("int"),
    "void*": VOID_P,
    "Py_ssize_t": ctc("ssize_t"),
    "char": ctc("char"),
    "char*": CHAR_P,
    "const char*": CHAR_P,
    "unsigned long": ctc("ulong"),
    "unsigned long long": ctc("ulonglong"),
    "unsigned int": ctc("uint"),
    "long long": ctc("longlong"),
    "size_t": ctc("size_t"),
    "double": ctc("double"),
    "long": ctc("long"),
    "uint64_t": ctc("uint64"),
    "int64_t": ctc("int64"),
    # docs have invalid definitions of wchar apparently
    "wchar*": WCHAR_P,
    "wchar_t*": WCHAR_P,
    "w_char*": WCHAR_P,
    "va_list": VOID_P,
    "wchar_t": WCHAR,
    "const wchar_t": WCHAR,
    "PyTypeObject": "PyTypeObject",
    "Py_UCS4": "Py_UCS4",
    "PyThreadState": "PyThreadState",
    "PyVarObject": "PyVarObject",
    "PyFrameObject": "PyFrameObject",
    "PyInterpreterState": "PyInterpreterState",
}

CT_TYPES = {
    "char_p": "StringLike",
    "wchar_p": "str",
    "wchar": "str",
    "long": "int",
    "longlong": "int",
    "size_t": "int",
    "ssize_t": "int",
    "int": "int",
    "uint64": "int",
    "int64": "int",
    "uint": "int",
    "ulong": "int",
    "ulonglong": "int",
    "py_object": "PyObjectLike",
    "void_p": "PointerLike",
    "char": "CharLike",
    "double": "int",
}

NEWLINE = "\n"

HARDCODED_NAMES: dict[str, str] = {
    "GC_IsTracked": "gc_is_tracked",
    "GC_Track": "gc_track",
    "GC_UnTrack": "gc_untrack",
    "GC_IsFinalized": "gc_is_finalized",
    "GC_Del": "gc_del",
}

NAME_GROUPS: list[str] = ["ASCII", "UTF", "UCS", "FS"]


def not_found(item: str, func: str) -> None:
    print("Not found...", item, "in", func)


def _write_autogen(file: str, text: str) -> None:
    with open(f"./src/pointers/{file}") as f:
        lines = f.read().split("\n")  # readlines was keeping the \n

    with open(f"./src/pointers/{file}", "w") as f:
        try:
            index = lines.index("# autogenerated")
        except ValueError:
            index = lines.index(
                "# autogenerated "
            )  # in case there's trailing whitespace

        f.write(
            "\n".join(lines[: index + 1]) + f"\n{text}",
        )


def _get_type(ctype: str, *, add_pointer: bool = False) -> str | None:
    typ = C_TYPES.get(ctype)

    if typ:
        return f"{typ if not add_pointer else f'ctypes.POINTER({typ})'}"
    else:
        if ctype.endswith("*"):
            index = ctype.index("*")
            ptrs = ctype[index:].count("*") + add_pointer
            join = ctype[:index]

            typ = C_TYPES.get(f"{join}*")

            if not typ:
                typ = C_TYPES.get(join)
            else:
                ptrs -= 1

            if not typ:
                return None

            typ = "".join(
                [
                    *["ctypes.POINTER(" for _ in range(ptrs)],
                    typ,
                    *[")" for _ in range(ptrs)],
                ]
            )
            return typ
    return None


def _gen_ct_bindings() -> dict[str, list[str]]:
    params: dict[str, list[str]] = {}

    out: str = ""
    resp = requests.get(
        f"{BASE_URL}/stable.html#stable-application-binary-interface",
    )
    soup = BeautifulSoup(resp.text, features="html.parser")
    ul = soup.find("ul", attrs={"class": "simple"})
    assert ul

    for tag in ul:
        if not isinstance(tag, Tag):
            continue

        p = tag.find("p", recursive=True)
        assert p
        a = p.find("a")

        if a:
            assert type(a) is Tag
            name: str = a.get_text().replace("()", "")
            href = a.attrs["href"]
            path = href[: href.find(".html")]

            if path not in PAGES:
                print("Loading page... ", path)
                PAGES[path] = BeautifulSoup(
                    requests.get(f"{BASE_URL}/{path}.html").text,
                    features="html.parser",
                )

            page = PAGES[path]
            signature: str = ""
            doc = page.find(id=f"c.{name}")
            assert doc, f"{page} {name}"

            for tg in doc:
                if isinstance(tg, str):
                    signature += tg if tg != "\n" else ""
                    continue

                text: str = tg.get_text()
                if text != "Â¶":
                    signature += text

            assert type(doc) is Tag
            parent = doc.parent
            assert parent

            minver_soup = parent.find(
                "span",
                attrs={"class": "versionmodified added"},
                recursive=True,
            )
            minver: str | None = None

            if minver_soup:
                minver = minver_soup.get_text()[:-1].split(" ")[-1]
                # this is super janky

            signature = signature.replace(" *", "* ").replace("* *", "** ")
            match = C_FUNC.match(signature)

            if match:
                params[name] = []
                group = match.group(1)
                ret = _get_type(group)

                if not ret:
                    not_found(group, name)
                    continue

                if match.group(12):
                    argtypes = ""
                else:
                    args = match.group(7)
                    if not args:
                        args = "void"
                    argtypes = ", ("

                    if args != "void":
                        for arg in args.split(", "):
                            arg_split = arg.split(" ")
                            argname = arg_split.pop(-1)
                            add_pointer: bool = False

                            if argname.endswith("[]"):
                                argname = argname[:-2]
                                add_pointer = True

                            params[name].append(argname if argname != "def" else "df")

                            join = " ".join(arg_split).replace(
                                "const ", ""
                            )  # we dont care about consts
                            typ = _get_type(join, add_pointer=add_pointer)

                            if not typ:
                                not_found(join, name)
                                continue

                            argtypes += typ + ","

                    argtypes += ")"

                out += f"# {signature}\n_register('{name}', {ret}{argtypes}{f', minver={DOUBLE_QUOTE}{minver}{DOUBLE_QUOTE},' if minver else ''})\n"
            else:
                ...
                # print(f"No match... {signature}")

    _write_autogen("_pyapi.py", out)
    return params


def map_type(typ: type["ctypes._CData"] | None) -> str:
    if not typ:
        return "None"
    name = typ.__name__

    if name.startswith("LP_"):
        return "PointerLike"

    return CT_TYPES[name[2:] if name != "py_object" else name]


def get_converter(data: str, typ: str) -> str:
    if typ == "StringLike":
        return f"make_string({data})"

    elif typ == "CharLike":
        return f"make_char({data})"

    elif typ == "Format":
        return f"make_format({data})"

    elif typ == "PyObjectLike":
        return f"_deref_maybe({data})"

    return data


def main():
    params = _gen_ct_bindings()
    while True:
        yn = input("regen api_bindings.py (y/n)? ").lower()

        if yn not in {"y", "n"}:
            continue

        if yn == "n":
            return
        break

    out: str = """raise Exception('autogenerating some things is too complicated or not possible! please manually go through and update the rest. you may delete this error when finished\n')"""
    from src.pointers._pyapi import API_FUNCS

    funcs: dict[str, list[str]] = {}

    for k, v in API_FUNCS.items():
        func = v[0]

        if not func:
            continue

        zip_params = (params[k], func.argtypes)

        if not func.argtypes:
            continue

        fparams = [f"{param}: {map_type(typ)}" for param, typ in zip(*zip_params)]
        restype: type["ctypes._CData"] = func.restype  # type: ignore

        name_split = k.split("_")
        section = name_split[0]

        if section not in funcs:
            funcs[section] = []

        origin_name = "_".join(name_split[1:])
        name = HARDCODED_NAMES.get(origin_name) or ""

        if not name:
            for i in NAME_GROUPS:
                if i in origin_name:
                    index = origin_name.index(i)
                    origin_name = origin_name.replace(
                        i,
                        f"{'_' if index else ''}{i.lower()}{'_' if (index + len(i)) != len(origin_name) else ''}",
                    )

            for index, i in enumerate(origin_name):
                lower: str = i.lower()

                if i.isupper():
                    name += ("_" if index else "") + lower
                else:
                    name += lower

            if name in {"or", "and", "import", "not", "is"}:
                name += "_"

        funcs[section].append(
            f"""
    # {k}
    @staticmethod
    def {name}({', '.join(fparams)}) -> {map_type(restype)}:
        return api_binding_base(API_FUNCS["{k}"], {', '.join([get_converter(i, map_type(typ)) for i, typ in zip(*zip_params)])})
"""
        )

    for k, v in funcs.items():
        out += f"""class {k}(_CallBase):
    {TRIPLE_QUOTE}Namespace containing API functions prefixed with `{k}_`{TRIPLE_QUOTE}
{NEWLINE.join(v)}
"""

    _write_autogen("api_bindings.py", out)


if __name__ == "__main__":
    main()
