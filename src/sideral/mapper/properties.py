from __future__ import annotations
from sideral.utils import abstract
from typing import Generator


@abstract
class Property:

    _null_value = None

    def __init__(self, attribute_name: str, strategy: strategy.load) -> None:
        self.attribute_name = attribute_name
        self.strategy = strategy

    @property
    def is_lazy(self) -> bool:
        if self.strategy != strategy.load.EAGER: 
            return True
        return False

    def get_attribute(self, element: object) -> any:
        return getattr(element, self.attribute_name) 

    def set_attribute(self, element: Proxy, value: any) -> None:
        raise NotImplementedError
    
    def set_null(self, element: Proxy) -> None:
        setattr(element, self.attribute_name, self._null_value)

    def load(self, proxy: Proxy) -> object:
        return self.strategy(self, proxy)

    def _post_execute_action(self, result: ResultSet) -> None:
        raise NotImplementedError



class Column(Property):

    def __init__(self, attribute_name: str, strategy: strategy.load, column: schema.Column) -> None:
        super().__init__(attribute_name, strategy)
        self.column = column

    def set_attribute(self, proxy: Proxy, value: any, mirror: bool = False) -> object:
        setattr(proxy, self.attribute_name, value)
        return proxy
    
    def build_select(self, id: any = ...) -> Select:
        sql = self.column.build_select()
        
        if id is not ...:
            sql.where(self.column.table.primary_key.column == id)
        
        return sql
    
    def _post_execute_action(self, result: ResultSet) -> Generator:
        yield next(result.main()).get_by(self.column)



@abstract
class Relationship(Property):
    owner: bool = False

    def __init__(self, 
        reference: Model, 
        attribute_name: str, 
        strategy: strategy.load, 
        mapping: str, 
        table: Table, 
        join_column: ForeignKey,
    ) -> None:
        super().__init__(attribute_name, strategy)
        self.reference = reference
        self.mapping = mapping
        self.table = table
        self.join_column = join_column
    
    @property
    def relative_key_column(self) -> Column:
        raise NotImplementedError
    
    @property
    def is_many_to_many(self) -> bool:
        return False

    # def build_select(self, id: any = ...) -> Select:
    #     sql = self.reference.build_select()
    #     if not self._related:
    #         sql \
    #         .columns(self.join_column.column) \
    #         .join(self.table, type = Join.RIGHT, on = self.join_column.column == self.join_column.reference)

    #     if id is not ...:
    #         sql.where(self.join_column.column == id)
        
    #     return sql

    def _post_execute_action(self, result: ResultSet) -> Generator:
        return Loader.load_on(rows = result.main(), model = self.reference, key = self.join_column.column)



class ToOne(Relationship):

    def set_attribute(self, proxy: Proxy, value: any, mirror: bool = False) -> object:
        setattr(proxy, self.attribute_name, value)
        if mirror and self.mapping:
            value.__class__.get_property(name = self.mapping).set_attribute(value, proxy) 
        return proxy
    
    def get_key(self, element: object) -> any:
        referenced_element = getattr(element, self.attribute_name)
        if referenced_element in (None, ...):
            return None
        else:
            return self.reference.identifier.get_attribute(referenced_element)


class ToMany(Relationship):

    _null_value = []

    def __init__(
        self, 
        reference: Model, 
        attribute_name: str, 
        strategy: strategy.load, 
        mapping: str, table: Table, 
        join_column: ForeignKey,
        secondary_table: Table = None, 
        secondary_join_column: ForeignKey = None,
    ) -> None:
        super().__init__(reference, attribute_name, strategy, mapping, table, join_column)
        self.secondary_table = secondary_table
        self.secondary_join_column = secondary_join_column

    @property
    def relative_key_column(self) -> Column:
        return self.secondary_join_column.column or self.reference.table.primary_key.column
    
    @property
    def is_many_to_many(self) -> bool:
        return bool(self.secondary_table)
    
    def build_select(self, id: any = ...) -> Select:
        sql = self.reference.build_select()

        if self.secondary_table:
            sql \
            .columns([self.secondary_join_column.column, self.join_column.column]) \
            .join(self.secondary_table, type = Join.RIGHT, on = self.secondary_join_column.column == self.secondary_join_column.reference) \
            .join(self.table, type = Join.INNER, on = self.join_column.column == self.join_column.reference)

        else:
            sql \
            .columns(self.join_column.column) \
            .join(self.table, type = Join.RIGHT, on = self.join_column.column == self.join_column.reference)

        if id is not ...:
            sql.where(self.join_column.column == id) 
        
        return sql

    def set_attribute(self, proxy: Proxy, value: any, mirror: bool = False) -> object:
        try:
            getattr(proxy.__element__, self.attribute_name).append(value)
        except AttributeError:
            setattr(proxy, self.attribute_name, [value])
        finally:
            if mirror and self.mapping:
                value.__class__.get_property(name = self.mapping).set_attribute(value, proxy)
            return proxy
    
    # def _post_execute_action(self, result: ResultSet) -> Generator:
    #     return Loader.load_on(rows = result.main(), model = self.reference, key = self.join_column.column if not self.secondary_join_column else self.secondary_join_column.column)


class OneToOne(ToOne):

    def build_select(self, id: any = ...) -> Select:
        sql = self.reference.build_select() \
              .columns([self.join_column.column]) \
              .join(self.table, type = Join.RIGHT, on = self.join_column.column == self.join_column.reference)

        if id is not ...:
            sql.where(self.join_column.column == id)
        
        return sql

    @property
    def relative_key_column(self) -> Column:
        return self.reference.table.primary_key.column
    

class ManyToOne(ToOne):
    owner: bool = True

    def build_select(self, id: any = ...) -> Select:
        sql = self.reference.build_select() \
              .columns([self.join_column.column]) \
              .join(self.table, type = Join.RIGHT, on = self.join_column.reference == self.join_column.column)

        if id is not ...:
            sql.where(self.table.primary_key.column == id)
        
        return sql
    
    @property
    def relative_key_column(self) -> Column:
        return self.table.primary_key.column
    
    @property
    def is_many_to_one(self) -> bool:
        return True





from .model import Model
from sideral import schema
from sideral import strategy
from sideral.query import Select
from sideral.query import Join
from sideral.schema import Table
from sideral.schema import ForeignKey
from sideral.proxy import Proxy
from sideral.result import ResultSet
from sideral.loader import Loader