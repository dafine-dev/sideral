from __future__ import annotations
from typing import Generator


class Table:

    _instances: dict[str, Table] = {}
    __slots__ = 'name', 'primary_key', '_columns', '_foreign_keys'

    def __new__(cls, name: str) -> Table:
        try:
            return cls._instances[name]
        except KeyError:
            table = object.__new__(cls)
            table.init(name)
            return table

    def __str__(self) -> str:
        return self.name
    
    def __hash__(self) -> int:
        return hash(self.name)

    def init(self, name: str) -> None:
        self.name = name
        self.primary_key = None
        self._columns = {}
        self._foreign_keys = {}

    def add_column(self, column: Column) -> None:
        column.table = self
        self._columns[column.key] = column

    def add_foreign_key(self, foreign_key: ForeignKey) -> None:
        self._foreign_keys[foreign_key.column.key] = foreign_key

    @property
    def columns(self) -> Generator[Column]:
        return self._columns.values()

    @property
    def foreign_keys(self) -> Generator[ForeignKey]:
        return self._foreign_keys.values()

    def get_column(self, name: str) -> Column:
        try:
            return self._columns[name]
        except KeyError:
            return None

    def get_foreign_key(self, name: str) -> ForeignKey:
        try:
            return self._foreign_keys[name]
        except KeyError:
            return None
    
    def get_alias(self, index: int) -> str:
        return f'{self.name}_{index}'

    def build_select(self) -> Select:
        return (
            Select()
            .columns(self.columns)
            .from_(self)
        )


class Column:

    __slots__ = 'name', 'table', 'auto_increment'
    
    def __init__(self, name: str, auto_increment: bool = False) -> None:
        self.name = name
        self.auto_increment = auto_increment
    
    def __str__(self) -> str: 
        return self.full_name

    def __eq__(self, other: any) -> str: 
        return SQLCondition(self, '=', other)

    def __gt__(self, other: any) -> str: 
        return SQLCondition(self, '>', other)

    def __ge__(self, other: any) -> str: 
        return SQLCondition(self, '>=', other)

    def __lt__(self, other: any) -> str: 
        return SQLCondition(self, '<', other)

    def __le__(self, other: any) -> str: 
        return SQLCondition(self, '<=', other)
    
    def __hash__(self) -> int: 
        return hash(self.full_name)

    @property
    def key(self) -> str:
        return self.name

    @property
    def full_name(self) -> str:
        return f'{self.table.name}.{self.name}'
    
    @property
    def alias(self) -> str:
        return f'{self.table.name}_{self.name}'
    
    def get_alias(self, query: Query) -> str:
        table_alias = ...
        try:
            table_alias = query._tables[self.table][query._index]
        except IndexError:
            table_alias = query._tables[self.table][-1]            
        except KeyError:
            return self.alias

        return f'{table_alias}.{self.name}'   

    def build_select(self) -> Select:
        return (
            Select()
            .columns(self)
            .from_(self.table)
        )
    

class ForeignKey:

    __slots__ = 'column'
    
    def __init__(self, column: Column) -> None:
        self.column = column


class PrimaryKey(ForeignKey):

    def __init__(self, column: Column) -> None:
        super().__init__(column)
    

class ForeignKey(ForeignKey):

    __slots__ = 'reference'

    def __init__(self, column: Column, reference: Column) -> None:
        super().__init__(column)
        self.reference = reference


from .query import Query, Select, format, SQLCondition