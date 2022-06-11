from collections.abc import Callable
from typing import ParamSpec, TypeVar

Class = TypeVar('Class')
_params = ParamSpec('_params')
_return = TypeVar('_return')

class private_list:
    ...


def set_persister_slot(_class: type):
    if '__slots__' in vars(_class):
        _class.__slots__.append('__persister__')


def constructor(constructor: Callable[_params, _return]) -> Callable[_params, _return]:
    
    def wrapper(*args: _params.args, **kwargs: _params.kwargs) -> _return:
        args[0].__persister__ = 'new persister'
        return constructor(args, kwargs)

    return wrapper

def getter():
    ...

def setter():
    ...

def deleter():
    ...

def _hash(attribute_name: str) -> int:
    
    def wrapper(self) -> int:
        return hash(getattr(self, attribute_name))
    
    return wrapper

def _eq(self, other: any) -> bool:
    _class = self.__class__
    
    if isinstance(other, _class):
        for column in _class.__columns__:
            try:
                if getattr(self, column) != getattr(other, column):
                    return False
            except AttributeError:
                return False
    else:
        return False

    return True


def _prepare_model_class(_class: type, sub_class: bool = False) -> None:
    _class.__eq__ = _eq
    
    for column in _class.__columns__:
        getattr(_class, column).map()
    
    if sub_class:
        _class.__columns__.extend(_class.__bases__[0].__columns__)
    