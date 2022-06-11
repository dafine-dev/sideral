from __future__ import annotations
from .test_info import test_info
from sideral import entity
from sideral import id
from sideral import column
from sideral import inheritance
from sideral import strategy
from sideral import derived_key
from sideral import load


@entity
@inheritance(type = strategy.JOINED_TABLE)
class Functionary:

    __test_schema__ = ['id', 'name']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'name', strategy = load.EAGER, column = 'name'),
    ]

    __test_relationships__ = []

    def __init__(self, id: int = ..., name: str = ...) -> None:
        self._id = id
        self._name = name
    
    @id
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, value) -> None:
        self._id = value
    
    @column
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value) -> None:
        self._name = value    


@derived_key(name = 'id')
@entity
@inheritance(type = strategy.JOINED_TABLE)
class Coordinator(Functionary):

    __test_schema__ = ['id', 'sector']

    __test_columns__ = [
        test_info(attribute_name = 'sector', strategy = load.EAGER, column = 'sector'),
    ]

    __test_relationships__ = []

    def __init__(self, id: int = ..., name: str = ..., sector: str = ...) -> None:
        super().__init__(id, name)
        self._sector = sector

    @column
    def sector(self) -> str:
        return self._sector
    
    @sector.setter
    def sector(self, sector: str) -> None:
        self._sector = sector
    

@derived_key(name = 'id')
@entity
class Manager(Coordinator):

    __test_schema__ = ['id', 'unit']

    __test_columns__ = [
        test_info(attribute_name = 'unit', strategy = load.LAZY, column = 'unit'),
    ]

    __test_relationships__ = []
    
    def __init__(self, id: int = ..., name: str = ..., sector: str = ..., unit: str = ...) -> None:
        super().__init__(id, name, sector)
        self._unit = unit

    @column(load = load.LAZY)
    def unit(self) -> str:
        return self._unit
    
    @unit.setter
    def unit(self, unit: str) -> None:
        self._unit = unit