from pointers import binds, Struct, StructPointer
import ctypes

dll = ctypes.CDLL("libc.so.6")


class Lconv(Struct):
    decimal_point: str
    thousands_sep: str
    grouping: str
    int_curr_symbol: str
    currency_symbol: str
    mon_decimal_point: str
    mon_thousands_sep: str
    mon_grouping: str
    positive_sign: str
    negative_sign: str
    frac_digits: str
    p_cs_precedes: str
    p_sep_by_space: str
    n_sep_by_space: str
    p_sign_posn: str
    n_sign_posn: str


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


dll.localeconv.restype = ctypes.POINTER(lconv)


@binds(dll.localeconv, struct=Lconv)
def localeconv() -> StructPointer[Lconv]:
    ...


print((~localeconv()).decimal_point)
