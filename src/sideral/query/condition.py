from __future__ import annotations

    


class SQLCondition:

    def __init__(self, column: Column, operator: str, value: any) -> None:
        self._column = column
        self._operator = operator
        self._value = value
    
    def __str__(self) -> str:
        return f'{self._column} {self._operator} {format(self._value)}'
    
    def to_string(self, query: Query = None, on: bool = False) -> str:
        if on:
            column1 = self._column.get_alias(query)
            query._index = 1
            column2 = self._value.get_alias(query)
            return f'{column1} {self._operator} {column2}'
        return f'{self._column.get_alias(query)} {self._operator} {format(self._value)}'



from sideral.schema import Column
from .builder import Query
from .utils import format