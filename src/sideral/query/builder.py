from __future__ import annotations
from typing import Iterator
from .utils import Join


class Query:
    
    sub_queries: list[Query]

    def __str__(self) -> str:
        return self.statement

    @property
    def statement(self) -> str: raise NotImplementedError

    def sub_query(self, query: Query) -> Query: raise NotImplementedError


class Select(Query):

    def __init__(self) -> None:
        self._join = ''
        self._where = []
        self._tables = hash_map()
        self._from_clause = ''
        self._order_by = ''
        self._columns = hash_map()
        self.sub_queries = []
        self._index = 0
    
    def columns(self, columns: Column | Iterator[Column]) -> Select:
        columns = (columns,) if isinstance(columns, Column) else columns
        
        for column in columns:
            try:
                self._columns[column].append(column)
            except KeyError:
                self._columns[column] = [column]

        return self

    def from_(self, table: Table) -> Select:
        self._from_clause += f' from {table} as {self._add_table(table)} '
        return self

    def join(self, table: Table, on: SQLCondition, type: Join = Join.INNER) -> Select:
        self._from_clause += f' {type.value} {table} as {self._add_table(table)} on {on.to_string(self, on = True)}'
        return self
    
    def where(self, *conditions: list[str]) -> Select:
        for condition in conditions: 
            self._where.append(condition)
        return self

    def order_by(self, column: Column) -> Select:
        self._order_by = f' order by {column.full_name} '
        return self

    def defer(self, columns: Iterator[Column]) -> Select:
        for column in columns: 
            del self._columns[column]
        return self
    
    def sub_query(self, query: Query) -> Query:
        self.sub_queries.append(query)

    def _add_table(self, table: Table) -> str:
        table_alias = ...
        if table in self._tables:
            aliases = self._tables[table]
            table_alias = table.get_alias(len(aliases) + 1)
            aliases.append(table_alias)
        else:
            table_alias = table.get_alias(1)
            self._tables[table] = [table_alias]

        return table_alias

    @property
    def statement(self) -> str:
        sql = ' select ' 

        for columns in self._columns.values():
            for index, column in enumerate(columns):
                self._index = index
                sql += f' {column.get_alias(self)} as {column.alias},'
        
        self._index = 0
        sql = sql[:-1]
        sql += self._from_clause
        if self._where:
            sql += ' where '
            sql += ''.join(f'{condition.to_string(self)} and ' for condition in self._where)[:-4]
        
        sql += self._order_by
        sql +=  '; '
        for query in self.sub_queries: sql += f'{query} ;'
        return sql 


class Insert(Query):
    
    def __init__(self) -> None:
        self._values = []

    def into(self, table: Table) -> Insert:
        self._table = table
        return self
    
    def values(self, values: Iterator[tuple[Column, any]]) -> Insert:
        for column, value in values:
            self._values.append((column, value))
        return self

    def on_duplicate_key(self) -> Insert:
        self._on_duplicate = True
        return self
    
    @property
    def statement(self) -> str:
        sql = ' insert'
        sql += f' into {self._table} ('
        sql += ''.join(f'{value[0]}, ' for value in self._values)[:-2]
        sql += ') values ('
        sql += ''.join(f'{format(value[1]) if value[1] not in (None, ...) else "default"}, ' for value in self._values)[:-2]
        sql += ') '

        if self._on_duplicate:
            sql += ' on duplicate key update '
            sql += ''.join(f'{value[0] == value[1]}, ' for value in self._values)[:-2]
        
        sql += '; '
        return sql

class Update(Query):
    
    def __init__(self) -> None:
        self._where = []

    def table(self, table: Table) -> Update:
        self._table = table
        return self

    def set(self, columns: list[tuple[Column, any]]) -> Update:
        self._columns = columns
        return self
    
    def where(self, *conditions: list[str]) -> Update:
        for condition in conditions:
            self._where.append(condition)
        return self
    
    @property
    def statement(self) -> str:
        sql = f'update {self._table} set '
        sql += ''.join(f'{column[0] == column[1]}, ' for column in self._columns)[:-2]
        sql += ' where '
        #add criteria class
        sql += ''.join(f'{condition} and ' for condition in self._where)[:-4]
        sql += '; '
        return sql


class Delete(Query):
    
    def __init__(self) -> None:
        self._where = []

    def from_(self, table: Table) -> Delete:
        self._from = table
        return self
    
    def where(self, *conditions: list[str]) -> Delete:
        for condition in conditions:
            self._where.append(condition)
        return self

    @property
    def statement(self) -> str:
        sql = 'delete '
        sql += f'from {self._from} where '
        #add criteria class
        sql += ''.join(f'{condition} and ' for condition in self._where)[:-4]
        sql += '; '
        return sql


from sideral.utils import hash_map
from sideral.schema import Table, Column
from .utils import format
from .condition import SQLCondition