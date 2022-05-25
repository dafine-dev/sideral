from __future__ import annotations
from sideral.utils import abstract, UNLOADED
from typing import Generator


class Model:

    __slots__ = '_class', '_table', '_columns', '_relationships', '_identifier_index', '_status'
    _instances: dict[str, Model] = {}

    def __new__(cls, _class: type) -> Model:
        try:
            return Model._instances[_class.__name__]
        except KeyError:
            model = object.__new__(cls)
            model.init(_class)
            return model
    
    def __init__(self, _class: type) -> None: ...

    def init(self, _class: type) -> None:
        self._class = _class
        self._columns = []
        self._relationships = UNLOADED
        self._identifier_index = None
        Model._instances[self.key] = self
    
    @property
    def key(self) -> str:
        return self._class.__name__

    @property
    def table(self) -> Table:
        return self._table
    
    @table.setter
    def table(self, table: Table) -> None:
        self._table = table
    
    @property
    def identifier(self) -> properties.Column:
        try:
            return self._columns[self._identifier_index]
        except KeyError:
            raise AttributeError("Id was never instatiated")
        
    
    @identifier.setter
    def identifier(self, id: properties.Column) -> None:
        self._columns.append(id)
        self._identifier_index = len(self._columns) - 1
    
    @property
    def base(self) -> Model: return None
    
    @property
    def subs(self) -> Generator[Model]: return []
    
    def columns(self, with_base: bool = True) -> Generator[properties.Column]:
        return (column for column in self._columns)
    
    def relationships(self, with_base: bool = True) -> Generator[properties.Relationship]:
        try:
            return (relationship for relationship in self._relationships)
        except UnloadedIterator:
            self._relationships = []
            for a in vars(self._class).values():
                if isinstance(a, relationships.relationship): a.map()
            return self.relationships()

    @property
    def properties(self) -> Generator[properties.Property]:
        for prop in self.columns(): yield prop
        for prop in self.relationships(): yield prop

    @property
    def discriminator(self) -> Column:
        raise AttributeError("Model doesn't have a discriminator")
    
    @property
    def discriminator_value(self) -> any:
        raise AttributeError("Model doesn't have a discriminator value")
    
    @property
    def proxy(self) -> type[Proxy]:
        return ProxyMeta(self)
    
    @property
    def persister(self) -> Persister:
        return Persister(self)

    def new(self) -> _class:
        return object.__new__(self._class)

    def add_relationship(self, relationship: properties.Relationship) -> None:
        self._relationships.append(relationship)
    
    def add_column(self, column: properties.Column) -> None:
        self._columns.append(column)
    
    def add_sub(self, model: Model) -> None:
        raise AttributeError("Can't add sub to this model")
    
    @classmethod
    def get(cls, _class: type) -> Model:
        try:
            return cls._instances[_class.__name__]
        except KeyError:
            raise Exception(f'{_class} is not a model.')

    def get_model(self, row: Row) -> Model:
        return Model(self._class)

    def build_select(self) -> Select:
        return (
            Select()
            .columns(self.table.columns)
            .from_(self.table)
            .defer(column_prop.column for column_prop in self.columns() if column_prop.is_lazy)
        )
    
    def build_insert(self) -> Insert:
        return Insert().into(self._table).on_duplicate_key()

    def build_update(self) -> Update:
        return Update().table(self._table)
    
    def build_delete(self) -> Delete:
        return Delete().from_(self._table)

@abstract
class ModelDecorator(Model):
    
    __slots__ = '_model'

    def __new__(cls, model: Model) -> Model:
        new_model = object.__new__(cls)
        new_model.init(model)
        return new_model

    def init(self, model: Model) -> None:
        self._model = model
        self._class = model._class
        Model._instances[model.key] = self

    @property
    def key(self) -> str:
        return self._model.key

    @property
    def table(self) -> Table:
        return self._model.table
    
    @table.setter
    def table(self, table: Table) -> None:
        self._model.table = table    
    
    @property
    def identifier(self) -> properties.Column:
        return self._model.identifier
    
    @identifier.setter
    def identifier(self, id: properties.Column) -> properties.Column:
        self._model.identifier = id

    def columns(self, with_base: bool = True) -> Generator[properties.Column]:
        return self._model.columns(with_base = with_base)
    
    def relationships(self, with_base: bool = True) -> Generator[properties.Relationship]:
        return self._model.relationships(with_base = with_base)

    @property
    def properties(self) -> Generator[properties.Property]:
        return self._model.properties

    @property
    def base(self) -> Model:
        return self._model.base
    
    @property
    def subs(self) -> Generator[Model]:
        return self._model.subs
    
    @property
    def discriminator(self) -> Column:
        return self._model.discriminator
    
    @property
    def discriminator_value(self) -> any:
        return self._model.discriminator_value
    
    @property
    def persister(self) -> Persister:
        return self._model.persister
    
    def add_relationship(self, relationship: properties.Relationship) -> None:
        return self._model.add_relationship(relationship)

    def add_column(self, column: properties.Column) -> None:
        return self._model.add_column(column)

    def add_sub(self, model: Model) -> None:
        return self._model.add_sub(model)

    def get_model(self, row: Row) -> Model:
        return self._model.get_model(row)

    def build_select(self) -> Select:
        return self._model.build_select()
    
    def build_insert(self) -> Insert:
        return self._model.build_insert()

    def build_update(self) -> Update:
        return self._model.build_update()

    def build_delete(self) -> Delete:
        return self._model.build_delete()
    
    def new(self) -> object:
        return self._model.new()


class BaseEntity(ModelDecorator):

    __slots__ = '_subs'
    
    def init(self, model: Model) -> None:
        super().init(model)
        self._subs = []

    @property
    def subs(self) -> Generator[Model]:
        for _class in self._subs:
            model = Model(_class)
            yield model
            for _sub in model.subs: yield _sub
    
    def add_sub(self, model: Model) -> None:
        self._subs.append(model._class)

    def build_select(self) -> Select:
        sql = super().build_select()
        for model in self.subs:
            table = model.table
            foreign_pk = table.get_foreign_key(name = table.primary_key.column.name)

            sql.columns(table.columns).defer(column_prop.column for column_prop in model.columns() if column_prop.is_lazy)
            sql.join(table, type = Join.LEFT, on = foreign_pk.column == foreign_pk.reference)

        return sql

    def get_model(self, row: Row) -> Model:
        model = super().get_model(row)
        for _class in self._subs:
            sub_model = Model(_class)
            if row.get_by(sub_model.table.primary_key.column):
                return sub_model.get_model(row)
        
        return model


class SubEntity(ModelDecorator):

    __slots__ = '_base'

    def init(self, model: Model) -> None:
        super().init(model)
        self.base.add_sub(self)
    
    @property
    def identifier(self) -> properties.Column:
        return self.base.identifier

    def columns(self, with_base: bool = True) -> Generator[properties.Column]:
        if with_base:
            for column in self.base.columns(): yield column
        
        for column in super().columns(): yield column

    def relationships(self, with_base: bool = True) -> list[properties.Relationship]:
        if with_base:
            for relationship in self.base.relationships(): yield relationship 
        
        for relationship in super().relationships(): yield relationship

    @property
    def properties(self) -> Generator[properties.Property]:
        for column in self.columns(): yield column
        for relationship in self.relationships(): yield relationship

    @property
    def base(self) -> Model:
        return Model(self._class.__bases__[0])

    @property
    def bases(self) -> Generator[Model]:
        base = self.base
        while base:
            yield base
            base = base.base
        
    @property
    def persister(self) -> Persister:
        return JoinedTablePersister(self)        

    def build_select(self) -> Select:
        sql = super().build_select()
        foreign_pk = self.table.get_foreign_key(name = self.table.primary_key.column.name)
        for model in self.bases:
            table = model.table

            sql.columns(table.columns).defer(column_prop.column for column_prop in model.columns() if column_prop.is_lazy)
            sql.join(table, type = Join.INNER, on = foreign_pk.column == foreign_pk.reference)
            
            foreign_pk = table.get_foreign_key(name = table.primary_key.column.name)

        return sql


class BaseSingleTable(ModelDecorator):
    
    __slots__  = '_subs', '_discriminator', '_discriminator_value'

    def init(self, model: Model) -> None:
        super().init(model)
        self._discriminator = None
        self._discriminator_value = None
        self._subs = {}

    @property
    def discriminator(self) -> Column:
        return self._discriminator
    
    @discriminator.setter
    def discriminator(self, column: Column) -> None:
        self.table.add_column(column)
        self._discriminator = column

    @property
    def discriminator_value(self) -> any:
        return self._discriminator_value

    @discriminator_value.setter
    def discriminator_value(self, value: any) -> None:
        self._discriminator_value = value
    
    @property
    def persister(self) -> Persister:
        return SingleTablePersister(self)

    def add_sub(self, model: Model) -> None:
        self._subs[model.discriminator_value] = model._class

    def get_model(self, row: Row) -> Model:
        value = row.get_by(self._discriminator)
        if self._discriminator_value == value:
            return self
        try:
            return Model(self._subs[value])
        except KeyError:
            raise Exception("Discriminator value doesn't have a equivalent class")


class SubSingleTable(ModelDecorator):

    __slots__ = '_discriminator_value'

    def init(self, model: Model) -> None:
        super().init(model)
        self._discriminator_value = None
    
    @property
    def identifier(self) -> properties.Column:
        return self.base.identifier

    @property
    def base(self) -> Model:
        return Model(super()._class.__bases__[0])

    @property
    def discriminator_value(self) -> any:
        return self._discriminator_value
    
    @discriminator_value.setter
    def discriminator_value(self, value: any) -> None:
        self._discriminator_value = value
        self.base.add_sub(self)
    
    @property
    def persister(self) -> Persister:
        return SingleTablePersister(self)

    @property
    def table(self) -> Table:
        return self.base.table

    @table.setter
    def table(self, table: Table) -> None:
        raise AttributeError("Can't change this class' table")
    
    def columns(self, with_base: bool = True) -> Generator[properties.Column]:
        if with_base:
            for column in self.base.columns(): yield column
        
        for column in super().columns(): yield column

    def build_select(self) -> Select:
        return self.base.build_select().where(self.base.discriminator == self._discriminator_value)
    
    def build_insert(self) -> Insert:
        sql = self.base.build_insert().values([(self.base.discriminator, self._discriminator_value)])
        return sql


from . import properties
from sideral.annotation import relationships
from sideral.schema import Table
from sideral.schema import Column
from sideral.result import Row
from sideral.query import Select, Join, Insert, Update, Delete
from sideral.proxy import Proxy, ProxyMeta
from sideral.errors import UnloadedIterator
from sideral.persister import Persister, JoinedTablePersister, SingleTablePersister