from __future__ import annotations
from .annotations import annotation
from .utils import _hash
from sideral.strategy import  load
from collections.abc import Callable
from typing import TypeVar, ParamSpec


_params = ParamSpec('_params')
_return = TypeVar('_return')


class column(annotation):

    def __init__(self, function: Callable[_params, _return] = None, name: str = None, load: load = load.EAGER) -> None:
        annotation.__init__(self, function, _name = name, load = load)
    
    def __set_name__(self, owner: type, name: str) -> None:
        super().__set_name__(owner, name)
        try:
            owner.__dict__['__columns__'].append(name)
        except KeyError:
            owner.__columns__ = [name]
        
    @property
    def name(self) -> str:
        return self._name or self.get.__name__
    
    def map(self) -> None:
        model = Model(self.owner)
        column = Column(name = self.name, auto_increment = False)
        model.table.add_column(column)
        model.add_column(properties.Column(attribute_name = self.attribute_name, strategy = self.load, column = column))


class id(column):

    def __init__(self, function: Callable[_params, _return] = None, name: str = None, auto_increment: bool = False) -> None:
        annotation.__init__(self, function, _name = name, auto_increment = auto_increment)

    def __set_name__(self, owner: type, name: str) -> None:
        super().__set_name__(owner, name)
        setattr(owner, '__hash__', _hash(name))

    def map(self) -> None:
        model = Model(self.owner)
        column = Column(name = self.name, auto_increment = self.auto_increment)
        model.table.add_column(column = column)
        model.table.primary_key = PrimaryKey(column = column)
        model.identifier = properties.Column(attribute_name = self.attribute_name, strategy = load.EAGER, column = column)


from sideral.mapper import Model
from sideral.mapper import properties
from sideral.schema import Column
from sideral.schema import PrimaryKey