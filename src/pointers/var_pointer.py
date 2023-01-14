import ast
import inspect
import pathlib
import warnings
from contextlib import suppress
from types import FrameType as Frame
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from _pointers import force_update_locals

from .base_pointers import BasePointer
from .exceptions import NullPointerError, VariableLifetimeError
from .util import NULL, Nullable, handle

T = TypeVar("T")

if hasattr(ast, "NamedExpr"):
    NamedExpr = ast.NamedExpr  # type: ignore
else:

    class NamedExpr:  # type: ignore
        ...


def _remove_indent(source: str) -> str:
    result: List[str] = []
    split = source.split("\n")

    if (not split[0].startswith(" ")) and (not split[0].startswith("\t")):
        return source

    last_indent_size: Optional[int] = None

    for line in split:
        if (not line.startswith(" ")) and (not line.startswith("\t")):
            break

        index = 0

        for i in line:
            if i not in {" ", "\t"}:
                break
            index += 1

        if (index != last_indent_size) and last_indent_size:
            result.append(line[last_indent_size:])
        else:
            result.append(line[index:])
        last_indent_size = index

    return "\n".join(result)


class VarPointer(BasePointer[T]):
    def __init__(self, name: str, frame: Frame) -> None:
        self.name: Optional[str] = name
        self._frame = frame
        self._address = id(~self)

    def _get_scope(self) -> Dict[str, Any]:
        if not self.name:
            raise NullPointerError("pointer is NULL")

        frame = self._frame

        if self.name in frame.f_globals:
            return frame.f_globals

        if self.name in frame.f_locals:
            return frame.f_locals

        raise VariableLifetimeError(f'variable "{self.name}" no longer exists')

    @handle
    def move(
        self,
        target: Union[T, "BasePointer[T]"],
        *,
        unsafe: bool = False,
    ) -> None:
        if unsafe:
            warnings.warn("unsafe has no effect on variable pointers")

        if not self.name:
            raise NullPointerError("pointer is NULL")

        scope = self._get_scope()

        if (scope is self._frame.f_locals) and (
            self._frame.f_locals is not self._frame.f_globals
        ):
            force_update_locals(
                self._frame,
                self.name,
                (
                    ~target
                    if isinstance(
                        target,
                        BasePointer,
                    )
                    else target
                ),
            )
        else:
            scope[self.name] = (
                ~target
                if isinstance(
                    target,
                    BasePointer,
                )
                else target
            )

    @property
    def address(self) -> Optional[int]:
        return self._address

    def _cleanup(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"VarPointer(name={self.name!r})"

    def dereference(self) -> T:
        if not self.name:
            raise NullPointerError("pointer is NULL")

        return self._get_scope()[self.name]

    def assign(self, value: Nullable[Union["VarPointer[T]", T]]) -> None:
        if value is NULL:
            self._address = 0
            self.name = None
            return

        frame = inspect.currentframe()
        assert frame
        assert frame.f_back

        if frame.f_back.f_globals == frame.f_globals:
            # it was called by __irshift__
            back = frame.f_back.f_back
            assert back
            txt = pathlib.Path(back.f_code.co_filename).read_text()
            expr = _remove_indent(
                "\n".join(txt.split("\n")[back.f_lineno - 1:]),
            )
            caller_scope = {**back.f_globals, **back.f_locals}
            augassign: Optional[ast.AugAssign] = None

            for node in ast.parse(expr).body:
                if (
                    isinstance(node, ast.AugAssign)
                    and isinstance(node.op, ast.RShift)
                    and isinstance(node.target, ast.Name)
                ):
                    with suppress(KeyError):
                        if caller_scope[node.target.id] is self:
                            augassign = node
                            break

            if not augassign:
                raise ValueError("failed to find ast.AugAssign")

            if not isinstance(augassign.value, ast.Name):
                raise TypeError(f"{value} does not have a variable name")

            self.name = augassign.value.id
            self._address = id(value)
            return

        self.name = _find_name(frame.f_back, value, self.assign)
        self._address = id(value)

    def __irshift__(
        self,
        value: Nullable[Union["VarPointer[T]", T]],
    ):
        self.assign(value)
        return self


def _check_call_expr(
    node: ast.AST, caller_scope: dict, caller: Callable[..., Any]
) -> Optional[ast.Call]:
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            with suppress(KeyError):
                call_func = caller_scope[node.func.id]

                if call_func == caller:
                    return node
        elif isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            with suppress(KeyError):
                obj = caller_scope[node.func.value.id]
                attr = getattr(obj, node.func.attr, None)

                if attr and (attr == caller):
                    return node
    return None


def _find_call_expr(
    node: ast.AST, caller_scope: dict, caller: Callable[..., Any]
) -> Optional[ast.Call]:
    if isinstance(node, ast.Assign):  # ptr = to_var_ptr(my_variable)
        node = node.value
    elif isinstance(node, ast.Expr):  # to_var_ptr(my_variable)
        node = node.value

    if hasattr(node, "value"):
        nd = _find_call_expr(node.value, caller_scope, caller)  # type: ignore
        if nd:
            return nd

    if hasattr(node, "args"):
        args = node.args  # type: ignore
        if not isinstance(args, ast.arguments):
            for expr in args:
                nd = _find_call_expr(expr, caller_scope, caller)
                if nd:
                    return nd
    return _check_call_expr(node, caller_scope, caller)


def _find_name(frame: Frame, value: Any, caller: Callable[..., Any]) -> str:
    txt = pathlib.Path(frame.f_code.co_filename).read_text()
    expr = _remove_indent("\n".join(txt.split("\n")[frame.f_lineno - 1:]))
    caller_scope = {**frame.f_globals, **frame.f_locals}
    call_expr: Optional[ast.Call] = None

    for node in ast.parse(expr).body:
        call_expr = _find_call_expr(node, caller_scope, caller)

        if call_expr:
            break

    if not call_expr:
        raise ValueError("failed to find ast.Call")

    param = call_expr.args[0]

    if not isinstance(param, (ast.Name, NamedExpr)):
        raise TypeError(f"{value} does not have a variable name")

    name_expr = param if isinstance(param, ast.Name) else param.target

    if not isinstance(name_expr, ast.Name):
        raise TypeError(f"{ast.dump(name_expr)} is not a name")

    return name_expr.id


def to_var_ptr(value: T) -> VarPointer[T]:
    frame = inspect.currentframe()
    assert frame
    assert frame.f_back
    name = _find_name(frame.f_back, value, to_var_ptr)
    return VarPointer(name, frame.f_back)
