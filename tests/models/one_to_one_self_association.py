from __future__ import annotations
from .test_info import test_info
from sideral import entity
from sideral import id
from sideral import column
from sideral import join
from sideral import one_to_one
from sideral import load


@entity
class Employee:

    __test_schema__ = ['id', 'name', 'id_supervisor']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'name', strategy = load.EAGER, column = 'name'),
    ]

    __test_relationships__ = [
        test_info(
            attribute_name = 'supervisor', 
            strategy = load.LAZY, 
            column = 'id_supervisor', 
            mapping = None, 
            reference = 'Employee',
            type = 'ManyToOne'),
    ]
    
    def __init__(self, id: int = ..., name: str = ..., supervisor: Employee = ...) -> None:
        self._id = id
        self._name = name
        self._supervisor = supervisor 
    
    @id
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, id: int) -> None:
        self._id = id
    
    @column
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @join('id_supervisor')
    @one_to_one(master = True, owner = True)
    def supervisor(self) -> Employee:
        return self._supervisor
    
    @supervisor.setter
    def supervisor(self, supervisor: Employee) -> None:
        self._supervisor = supervisor