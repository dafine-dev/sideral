from __future__ import annotations
from functools import partial
from enum import Enum
from sideral.utils import abstract
from collections.abc import Callable
from typing import TypeVar, ParamSpec, get_type_hints


_params = ParamSpec('_params')
_return = TypeVar('_return')


class strategy(Enum):

    SINGLE_TABLE = 'single_table'
    JOINED_TABLE = 'joined_table'



@abstract
class annotation:
    
    def __init__(self, function: Callable[_params, _return] = None, **kwargs) -> None: 
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        self.__call__(function)

    def __call__(self, function: Callable[_params, _return]) -> annotation:
        self.get = function
        return self

    def __set_name__(self, owner: type, name: str) -> None:
        self.owner = owner
        self.attribute_name = name

    def __get__(self, obj, objtype) -> _return:
        if obj is None:
            return self

        return self.get(obj)    

    def __set__(self, obj, value) -> None:
        self.set(obj, value)
    
    def __delete__(self, obj) -> None:
        return self.delete(obj)

    def getter(self, function: Callable[_params, _return]) -> annotation:
        self.get = function
        return self
    
    def setter(self, function: Callable[_params, _return]) -> annotation:
        self.set = function
        return self
    
    def deleter(self, function: Callable[_params, _return]) -> annotation:
        self.delete = function
        return self 
    


def join(column_name: str) -> Callable[_params, _return]:

    def wrapper(relation: relationship) -> relationship:
        relation._join_column = column_name
        relation._join_setter = True
        return relation
    
    return wrapper


def counter_join(column_name: str) -> Callable[_params, _return]:

    def wrapper(relation: relationship) -> relationship:
        relation._counter_join_column = column_name
        relation._join_setter = True
        return relation
    
    return wrapper


def join_table(name: str) -> Callable[_params, _return]:

    def wrapper(relation: relationship) -> relationship:
        relation._join_table = name
        relation._join_setter = True
        return relation
    
    return wrapper


Class = TypeVar('Class')


def entity(_class: Class = None, name: str = None) -> Class:

    if _class is None:
        return partial(entity, name = name)
    
    table = Table(name = name or _class.__name__)
    model = Model(_class)
    model.table = table

    _prepare_model_class(_class)

    return _class

        

def subclass(_class: Class) -> Class:
    SubSingleTable(Model(_class))

    _prepare_model_class(_class, sub_class = True)

    return _class


def inheritance(_class: Class = None, type: strategy = strategy.SINGLE_TABLE) -> Class:
    
    if _class is None:
        return partial(inheritance, type = type)
    
    match type:
        
        case strategy.JOINED_TABLE:
            BaseEntity(Model(_class))
        case strategy.SINGLE_TABLE:
            BaseSingleTable(Model(_class))
        case _:
            raise Exception("Unknown strategy")
    
    return _class



def derived_key(_class: Class = None, name: str = None) -> Class:

    if _class is None:
        return partial(derived_key, name = name)
    
    _prepare_model_class(_class, sub_class = True)
    model = SubEntity(Model(_class))
    c = Column(name = name or f'id_{model.table.name}', auto_increment = False)
    model.table.add_column(c)
    model.table.primary_key = PrimaryKey(column = c)
    model.table.add_foreign_key(ForeignKey(column = c, reference = model.base.table.primary_key.column))


    return _class



def discriminator(name: str = ..., value: any = ...) -> Callable[[Class], Class]:

    def wrapper(_class: Class) -> Class:
    
        model = Model(_class)
        if name is not ...:
            model.discriminator = Column(name = name, auto_increment = False)
        if value is not ...: 
            model.discriminator_value = value

        return _class
    
    return wrapper

    




from .relationships import relationship
from .column import column
from sideral.mapper import Model
from sideral.mapper import BaseEntity
from sideral.mapper import SubEntity
from sideral.mapper import BaseSingleTable
from sideral.mapper import SubSingleTable
from sideral.schema import ForeignKey, PrimaryKey, Table
from sideral.schema import Column
from sideral.schema import ForeignKey
from .utils import _prepare_model_class