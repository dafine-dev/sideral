from __future__ import annotations
from .utils import metaclass
from typing import NewType, TYPE_CHECKING

if TYPE_CHECKING:
    from .mapper import Model    
    from .mapper import Property


def _constructor(self, element: object) -> None:
    object.__setattr__(self, '__element__', element)

def _getter(self, item):
    try:
        return self.__properties__[item].load(self)
    except KeyError: 
        raise AttributeError

def _setter(self, item, value):
    setattr(self.__element__, item, value)

def _str(self) -> str:
    return str(self.__element__)

def _eq(self, other) -> bool:
    return self.__element__.__eq__(other)

def _eq(self, other) -> bool:
    _class = self.__class__.__bases__[0]
    if isinstance(other, self.__class__.__bases__[0]):
        for column in _class.__columns__:
            if getattr(self, column) != getattr(other, column):
                return False
    else:
        return False
    
    return True


@metaclass
class ProxyMeta(type):

    __model__: Model
    __element__: __model__._class
    __properties__: dict[str, Property]

    _instances: dict[str, Proxy] = {}

    def __new__(cls, model: Model) -> None:
        try:
            return cls._instances[model._class.__name__]
        except KeyError:

            attrs = {
                '__model__': model,
                '__properties__' : {prop.attribute_name: prop for prop in model.properties},
                '__init__': _constructor,
                '__getattr__': _getter,
                '__setattr__': _setter,
                '__str__': lambda self: str(self.__element__),
                '__eq__': _eq,
                '__hash__': lambda self: self.__element__.__hash__()
            }            

            return super().__new__(cls, f'{model._class.__name__}', (model._class,), attrs)
    
    def get_property(cls, name: str) -> Property:
        return cls.__properties__[name]



Proxy = NewType("Proxy", ProxyMeta)