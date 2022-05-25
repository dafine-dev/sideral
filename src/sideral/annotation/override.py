from __future__ import annotations
from collections.abc import Callable
from typing import ParamSpec, TypeVar


_params = ParamSpec('_params')
_return = TypeVar('_return')


class _Override:

    _functions: dict[str, list[Callable[_params, _return]]] = {}

    def __init__(self, name: str,) -> None:
        self._name = name
        self._return = int

    def add(self, function: Callable[_params, _return], index: int) -> _Override:
        if self._name in self._functions:
            self._functions[self._name][index] = function
        else:
            self._functions[self._name] = [None, None, None]
            self._functions[self._name][index] = function

        return self

    def __set_name__(self, owner, name) -> property:
        setattr(owner, name, property(*_Override._functions[name]))
        del self._functions[name]



def getter(function: Callable[_params, _return]):
    return _Override(function.__name__).add(function, index = 0)

def setter(function: Callable[_params, _return]):
    return _Override(function.__name__).add(function, index = 1)
    
def deleter(function: Callable[_params, _return]):
    return _Override(function.__name__).add(function, index = 2)
