from __future__ import annotations

from typing import Any, TypeVar

T = TypeVar("T")


class NULL:
    """Sentinel value for a NULL."""


Nullable = T | type[NULL]


def address_of(obj: Nullable[Any]) -> int:
    if obj is NULL:
        return 0

    return id(obj)
