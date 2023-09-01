import ctypes
from abc import ABC, abstractmethod
from typing import Any


class CTStruct:
    def __init__(self) -> None:
        assert type(self) != CTStruct
        self._map: dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:
        map = super().__getattribute__("_map")
        attr = map.get()
