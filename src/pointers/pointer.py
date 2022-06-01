import ctypes
from typing import (
    Generic,
    TypeVar,
    Type,
    Iterator,
    Union,
    Any,
    Mapping,
    Callable
)

from typing_extensions import ParamSpec
from contextlib import suppress
import faulthandler
from io import UnsupportedOperation
import sys
import gc
from .exceptions import (
    DereferenceError,
    IncorrectItemExpectedForSubscriptError,
    MethodNotInheritedError
)

__all__ = ("Pointer", "to_ptr", "dereference_address", "dereference_tracked")


def dereference_address(address: int) -> Any:
    """Get the PyObject at the given address."""
    return ctypes.cast(address, ctypes.py_object).value # 1.15 µs since ctypes is in CPython


def dereference_tracked(address: int) -> Any:
    """Dereference an object tracked by the garbage collector."""
    for obj in gc.get_objects(): # 13.5 ms + more as gc collects more obj to iterate, also NRQ since gc destroys obj at creation (deref is destroyed on __rshift__)
        if id(obj) == address:
            return obj

    raise DereferenceError(
        f"address {hex(address)} does not exist (probably removed by the garbage collector)"  # noqa
    )


with suppress(
    UnsupportedOperation
):  # in case its running in idle or something like that
    faulthandler.enable()

T = TypeVar("T")
A = TypeVar("A")
P = ParamSpec("P")


class Pointer(Generic[T]):
    """Base class representing a pointer."""

    def __init__(self, address: int, typ: Type[T]) -> None:
        self._address = address
        self._type = typ
        #self._tracked = tracked (nrq, the pointer acts to track.)

    @property
    def tracked(self) -> bool:
        """Whether the pointed object is tracked by the garbage collector."""
        return self._tracked

    @property
    def address(self) -> int:
        """Address of the pointer."""
        return self._address

    @property
    def type(self) -> Type[T]:
        """Type of the pointer."""
        return self._type

    def __repr__(self) -> str:
        return (
            f"<pointer to {self.type.__name__} object at {hex(self.address)}>"  # noqa
        )

    def __rich__(self):
        return f"<pointer to [green]{self.type.__name__}[/green] object at [cyan]{hex(self.address)}[/cyan]>"  # noqa

    def __str__(self) -> str:
        return hex(self.address)

    def dereference(self) -> T:
        """Dereference the pointer.""" # Dereference without the gc is much faster (1.15 µs vs 13.5 ms)
        return dereference_address(self.address)  # noqa

    def __iter__(self) -> Iterator[T]:
        """Dereference the pointer."""
        return iter({self.dereference()})

    def __invert__(self) -> T:
        """Dereference the pointer."""
        return self.dereference()

    def assign(self, new: "Pointer[T]") -> None:
        """Point to a different address."""
        if new.type is not self.type:
            raise ValueError("new pointer must be the same type")

        self._address = new.address

    def __rshift__(self, value: Union["Pointer[T]", T]):
        """Point to a different address."""
        self.assign(value if isinstance(value, Pointer) else to_ptr(value))
        return self

    def move(self, data: "Pointer[T]") -> None:
        """Move data from another pointer to this pointer. Very dangerous, use with caution."""  # noqa
        if data.type is not self.type:
            raise ValueError("pointer must be the same type")

        deref_a: T = ~data
        deref_b: T = ~self

        bytes_a = (ctypes.c_ubyte * sys.getsizeof(deref_a)) \
            .from_address(data.address)
        bytes_b = (ctypes.c_ubyte * sys.getsizeof(deref_b)) \
            .from_address(self.address)

        ctypes.memmove(bytes_b, bytes_a, len(bytes_a))

    def __lshift__(self, data: Union["Pointer[T]", T]):
        """Move data from another pointer to this pointer. Very dangerous, use with caution."""  # noqa
        self.move(data if isinstance(data, Pointer) else to_ptr(data))
        return self


    def __getitem__(self, item: Mapping[Any, A]) -> A:
        deref: T = ~self

        subscriptable = [Pointer, dict]
        referencable = [tuple, int, str, list]

        if hasattr(deref, '__getitem__'):
            return deref[item]  # type: ignore

        elif hasattr(deref, '__iter__'):
            if (type(item) in referencable) and (type(deref) in subscriptable):  # noqa
                return deref[item]  # type: ignore
            else:
                raise IncorrectItemExpectedForSubscriptError(
                    """subscript with an incorrect object, wrong item type for referenced PyObject."""
                )
        else:
            raise MethodNotInheritedError(
                f'"{type(deref).__name__}" object does not support item subscription.'  # noqa
            )

    def __setitem__(self, item: Mapping[Any, A], replace: A) -> None:
        deref: T = ~self

        if hasattr(deref, '__setitem__'):
            deref[item] = replace  # type: ignore
        else:
            raise MethodNotInheritedError(
                f'"{type(deref).__name__}" object does not support item assignment.'  # noqa
            )

    def __ilshift__(self, func: Callable[..., T]) -> None:
        """
        Apply a function on a pointer and re-point to result. Must return same data-type. Access byteshift via lambda x, y: x << y
        eg. x = 4
            ptr = to_ptr(x)
            ptr <<= lambda y: y ** 2
            >>> ~ptr
            16
        """
        deref = ~self
        shift = to_ptr(func(deref)) # type: ignore
        self.assign(shift)
        return self

    def __irshift__(self, func: Callable[..., T]) -> None:
        raise MethodNotInheritedError(
            f'"{type(deref).__name__}" object does not support >>='  # noqa
        )

    def __abs__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__abs__'):
            return deref.__abs__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__abs__'" # noqa
            )

    def __add__(self, other: Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__add__') &\
           hasattr(other, '__add__'):
            if isinstance(other, Pointer):
                deref_b: T = ~other
                return (deref_a + deref_b) # type: ignore
            else:
                return (deref_a + other)
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__add__'" # noqa
            )

    def __and__(self, other: Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__and__') &\
           hasattr(other, '__and__'):
            if isinstance(other, Pointer):
                deref_b: T = ~other
                return (deref_a & deref_b) # type: ignore
            else:
                return (deref_a & other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__and__'" # noqa
            )

    def __bool__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__bool__'):
            return deref.__bool__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__bool__'" # noqa
            )

    def __complex__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__complex__'):
            return deref.__complex__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__complex__'" # noqa
            )


    def __dlpack__(self) -> None: # inherited by np
        deref: T = ~self

        if hasattr(deref, '__dlpack__'):
            return deref.__dlpack__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__dlpack__'" # noqa
            )

    def __eq__(self, other: Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__eq__') &\
           hasattr(other, '__eq__'):
            if isinstance(other, Pointer):
                deref_b: T = ~other
                return deref_a == deref_b # type: ignore
            else:
                return deref_a == other # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__eq__'" # noqa
            )

    def __float__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__float__'):
            return float(deref) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__float__'" # noqa
            )

    def __format__(self, string: str) -> A:
        deref: T = ~self

        if hasattr(deref, '__format__'):
            return deref.__format__(string) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__format__'" # noqa
            )

    def __ge__(self, other: Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__ge__') &\
           hasattr(other, '__ge__'):
            if isinstance(other, Pointer):
                deref_b: T = ~other
                return deref_a >= deref_b # type: ignore
            else:
                return deref_a >= other # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__ge__'" # noqa
            )

    def __gt__(self, other: Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__gt__') &\
           hasattr(other, '__gt__'):
            if isinstance(other, Pointer):
                deref_b: T = ~other
                return deref_a > deref_b # type: ignore
            else:
                return deref_a > other # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__gt__'" # noqa
            )

    def __hash__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__hash__'):
            return deref.__hash__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__hash__'" # noqa
            )

    def __hex__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__hex__') :
            return deref.__hex__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__hex__'" # noqa
            )

    def __int__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__int__'):
            return deref.__int__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__int__'" # noqa
            )

    def __index__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__index__'):
            return deref.__index__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__index__'" # noqa
            )

    def __le__(self, other: Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__le__') &\
           hasattr(other, '__le__'):
            if isinstance(other, Pointer):
                deref_b: T = ~other
                return (deref_a <= deref_b) # type: ignore
            else:
                return (deref_a <= other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__le__'" # noqa
            )

    def __len__(self) -> int:
        deref: T = ~self

        if hasattr(deref, '__len__'):
            return len(deref)

    def __lt__(self, other: Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__lt__') &\
           hasattr(other, '__lt__'):
            if isinstance(other, Pointer):
                deref_b: T = ~other
                return (deref_a < deref_b) # type: ignore
            else:
                return (deref_a < other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__lt__'" # noqa
            )

    def __matmul__(self, other : Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__matmul__') &\
           hasattr(other, '__matmul__'):
            if isinstance(other, Pointer):
                deref_b = ~other
                return deref_a @ deref_b # type: ignore
            else:
                return deref_a @ other # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__matmul__'" # noqa
            )

    def __mod__(self, other : Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__mod__') &\
           hasattr(other, '__mod__'):
            if isinstance(other, Pointer):
                deref_b = ~other
                return deref_a % deref_b # type: ignore
            else:
                return deref_a % other # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__mod__'" # noqa
            )

    def __mul__(self, other : Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__mul__') &\
           hasattr(other, '__mul__'):
            if isinstance(other, Pointer):
                deref_b = ~other
                return (deref_a * deref_b) # type: ignore
            else:
                return (deref_a * other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__mul__'" # noqa
            )

    def __ne__(self, other : Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__ne__') &\
           hasattr(other, '__ne__'):
            if isinstance(other, Pointer):
                deref_b = ~other
                return (deref_a != other) # type: ignore
            else:
                return (deref_a != other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__ne__'" # noqa
            )

    def __neg__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__neg__'):
            return deref.__neg__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__neg__'" # noqa
            )

    def __nonzero__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__nonzero__'):
            return deref.__nonzero__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__nonzero__'" # noqa
            )

    def __oct__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__oct__'):
            return deref.__oct__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__oct__'" # noqa
            )

    def __or__(self, other : Union["Pointer[T]", A]) -> T:
        deref_a: T = ~self

        if hasattr(deref_a, '__or__') &\
           hasattr(other, '__or__'):
            if isinstance(other, Pointer):
                deref_b = ~other
                return (deref_a | deref_b) # type: ignore
            else:
                return (deref_a | other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__or__'" # noqa
            )

    def __pos__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__pos__'):
            return deref.__pos__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__pos__'" # noqa
            )


    def __pow__(self, other : Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__pow__') &\
           hasattr(other, '__pow__'):
            if isinstance(other, Pointer):
                deref_b = ~other
                return (deref_a ** deref_b) # type: ignore
            else:
                return (deref_a ** other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__pow__'" # noqa
            )

    def __truediv__(self, other: Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__truediv__') &\
           hasattr(other, '__truediv__'):
            if isinstance(other, Pointer):
                deref_b = ~other
                return (deref_a // deref_b) # type: ignore
            else:
                return (deref_a // other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__truediv__'" # noqa
            )

    def __trunc__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__trunc__'):
            return deref.__trunc__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__trunc__'" # noqa
            )

    def __unicode__(self) -> A:
        deref: T = ~self

        if hasattr(deref, '__unicode__'):
            return deref.__unicode__() # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref).__name__} has no attribute '__unicode__'" # noqa
            )

    def __rxor__(self, other : Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__rxor__') &\
           hasattr(other, '__rxor__'):
            if isinstance(other, Pointer):
                deref_b = ~other
                return deref_a.__rxor__(deref_b) # type: ignore
            else:
                return deref_a.__rxor__(other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__rxor__'" # noqa
            )

    def __xor__(self, other : Union["Pointer[T]", A]) -> A:
        deref_a: T = ~self

        if hasattr(deref_a, '__xor__') &\
           hasattr(other, '__xor__'):
            if isinstance(other, Pointer):
                deref_b = ~other
                return (deref_a ^ deref_b) # type: ignore
            else:
                return (deref_a ^ other) # type: ignore
        else:
            raise MethodNotInheritedError(
                f"{type(deref_a).__name__} has no attribute '__xor__'" # noqa
            )

    def __iadd__(self, other: Union["Pointer[T]", A]) -> None:
        if hasattr(other, '__add__'): # no need to check if ptr since ptr will use deref at __add__
            self << (self + other)
        else:
            raise MethodNotInheritedError(
                f"{type(~self).__name__} has no attribute '__iadd__'" # noqa
            )

    def __iand__(self, other: Union["Pointer[T]", A]) -> None:
        if hasattr(other, '__and__'):
            self << (self & other)
        else:
            raise MethodNotInheritedError(
                f"{type(~self).__name__} has no attribute '__iand__'" # noqa
            )

    def __idiv__(self, other: Union["Pointer[T]", A]) -> None:
        if hasattr(other, '__mul__'):
            self << (self / other)
        else:
            raise MethodNotInheritedError(
                f"{type(~self).__name__} has no attribute '__idiv__'" # noqa
            )

    def __ifloordiv__(self, other: Union["Pointer[T]", A]) -> None:
        if hasattr(other, '__mul__'):
            self << (self // other)
        else:
            raise MethodNotInheritedError(
                f"{type(~self).__name__} has no attribute '__ifloordiv__'" # noqa
            )

    def __imod__(self, other: Union["Pointer[T]", A]) -> None:
        if hasattr(other, '__div__'):
            self << (self % other)
        else:
            raise MethodNotInheritedError(
                f"{type(~self).__name__} has no attribute '__imod__'" # noqa
            )

    def __imul__(self, other: Union["Pointer[T]", A]) -> None:
        if hasattr(other, '__mul__'):
            self << (self * other)
        else:
            raise MethodNotInheritedError(
                f"{type(~self).__name__} has no attribute '__imul__'" # noqa
            )

    def __ior__(self, other: Union["Pointer[T]", A]) -> None:
        if hasattr(other, '__or__'):
            self << (self | other)
        else:
            raise MethodNotInheritedError(
                f"{type(~self).__name__} has no attribute '__ior__'" # noqa
            )

    def __ipow__(self, other: Union["Pointer[T]", A]) -> None:
        if hasattr(other, '__mul__'):
            self << (self ** other)
        else:
            raise MethodNotInheritedError(
                f"{type(~self).__name__} has no attribute '__ipow__'" # noqa
            )

    def __isub__(self, other: Union["Pointer[T]", A]) -> None:
        if hasattr(other, '__sub__'):
            self << (self - other)
        else:
            raise MethodNotInheritedError(
                f"{type(~self).__name__} has no attribute '__isub__'" # noqa
            )

def to_ptr(val: T) -> Pointer[T]:
    """Convert a value to a pointer."""
    return Pointer(id(val), type(val)) # gc.is_tracked(val) nrq if only casting to address - if kept locally gc will track & destroy intermediate objects
