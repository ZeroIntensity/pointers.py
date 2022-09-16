from .structure import Struct

__all__ = (
    "Tm",
    "DivT",
    "LDivT",
    "Lconv",
)


class Tm(Struct):
    tm_sec: int
    tm_min: int
    tm_hour: int
    tm_mday: int
    tm_mon: int
    tm_year: int
    tm_wday: int
    tm_yday: int
    tm_isdst: int


class DivT(Struct):
    quot: int
    rem: int


class LDivT(DivT):
    pass


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
