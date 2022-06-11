from __future__ import annotations
from collections.abc import Callable
from typing import ParamSpec, TypeVar, get_args, get_type_hints

from .annotations import annotation
from sideral.utils import abstract
from sideral.strategy import  load


_params = ParamSpec('_params')
_return = TypeVar('_return')


@abstract
class relationship(annotation):

    def __init__(self, function: Callable[_params, _return] = None, mapping: str = None, master: bool = False, load: load =  load.LAZY) -> None:
        super().__init__(function, mapping = mapping, master = master, _join_column = None, load = load)

    @property
    def reference(self) -> type:
        return get_type_hints(self.get)['return']
    
    def setup(self) -> None:
        ...



class one_to_many(relationship):

    @property
    def reference(self) -> type:
        try: 
            return get_args(super().reference)[0]
        except NameError:
            raise ReferenceNotInstantiated
    
    @property
    def join_column(self) -> str:
        default_join_column = f'id_{Model(self.owner).table.name}'
        try:
            return self._join_column or getattr(self.reference, self.mapping)._join_column or default_join_column
        except TypeError:
            return default_join_column


    def setup(self) -> None:
        model = Model(self.owner)
        reference = Model(self.reference)
        
        column = Column(name = self.join_column, auto_increment = False)
        fk = ForeignKey(column = column, reference = model.table.primary_key.column)
        
        reference.table.add_column(column)
        reference.table.add_foreign_key(fk)
        
        relationship = properties.ToMany(
            reference = reference, 
            attribute_name = self.attribute_name, 
            strategy = self.load,
            mapping = self.mapping,
            table = model.table,
            join_column = fk,
        )
        model.add_relationship(relationship)
        
        if self.master:
            InsertEntityEvent(model).add_listener(PersistAssociationEventListener(relationship))



class many_to_one(relationship):

    @property
    def reference(self) -> type:
        try: 
            return super().reference
        except NameError: 
            raise ReferenceNotInstantiated

    @property
    def join_column(self) -> str:
        default_join_column = f'id_{Model(self.reference).table.name}'
        try:
            return self._join_column or getattr(self.reference, self.mapping)._join_column or default_join_column
        except TypeError:
            return default_join_column
    

    def setup(self) -> None:
        model = Model(self.owner)
        reference = Model(self.reference)

        column = Column(name = self.join_column, auto_increment = False)
        fk = ForeignKey(column = column, reference = reference.table.primary_key.column)

        model.table.add_column(column)
        model.table.add_foreign_key(fk)

        relationship = properties.ManyToOne(
            reference = reference,
            attribute_name = self.attribute_name,
            strategy = self.load,
            mapping = self.mapping,
            table = model.table,
            join_column = fk,
        )

        if not self.master:
            relationship.owner = False

        model.add_relationship(relationship)



class one_to_one(relationship):
 
    def __init__(self, function: Callable[_params, _return] = None, mapping: str = None, master: bool = False, load: load =  load.LAZY, owner: bool = False) -> None:
        super().__init__(function, mapping, master, load)
        self._join_owner = owner

    # def __set_name__(self, owner: type, name: str) -> None:
    #     super().__set_name__(owner, name)
    #     try:
    #         self._join_owner = not getattr(self.reference, self.mapping)
    #     except (ReferenceNotInstantiated, TypeError):
    #         self._join_owner = self._join_owner

    @property
    def reference(self) -> type:
        try: 
            return super().reference
        except NameError: 
            raise ReferenceNotInstantiated

    @property
    def join_column(self) -> str:
        default_join_column = f'id_{Model(self.owner).table.name if self.master else Model(self.reference).table.name}'
        try:
            return self._join_column or getattr(self.reference, self.mapping)._join_column or default_join_column
        except TypeError:
            return default_join_column
        
    def setup(self) -> None:
        model = Model(self.owner)
        reference = Model(self.reference)

        column = Column(name = self.join_column, auto_increment = False)

        relationship = ...

        if self._join_owner:
            model.table.add_column(column)
            fk = ForeignKey(column = column, reference = reference.table.primary_key.column)
            relationship = properties.ManyToOne(
                reference = reference,
                attribute_name = self.attribute_name,
                strategy = self.load,
                mapping = self.mapping,
                table = model.table,
                join_column = fk,
            )
        else:
            reference.table.add_column(column)
            fk = ForeignKey(column = column, reference = model.table.primary_key.column)
            relationship = properties.OneToOne(
                reference = reference,
                attribute_name = self.attribute_name,
                strategy = self.load,
                mapping = self.mapping,
                table = model.table,
                join_column = fk,
            )

            if self.master:
                InsertEntityEvent(model).add_listener(PersistAssociationEventListener(relationship))

        model.add_relationship(relationship)




class many_to_many(relationship):

    def __init__(self, function: Callable[_params, _return] = None, mapping: str = None, master: bool = False, load:  load =  load.LAZY) -> None:
        super().__init__(function, mapping = mapping, master = master, load = load)
        self._counter_join_column = None
        self._join_table = None

    @property
    def reference(self) -> type:
        try: 
            return get_args(super().reference)[0]
        except NameError: 
            raise ReferenceNotInstantiated

    @property
    def join_table(self) -> str:
        table_names = [Model(self.owner).table.name, Model(self.reference).table.name]
        table_names.sort()
        default_join_table = f'{table_names[0]}_{table_names[1]}'

        try:
            return self._join_table or getattr(self.reference, self.mapping)._join_table or default_join_table
        except TypeError:
            return default_join_table
        
    @property
    def join_column(self) -> str:
        default_join_column = f'id_{Model(self.owner).table.name}'
        try:
            return self._join_column or getattr(self.reference, self.mapping)._counter_join_column or default_join_column
        except TypeError:
            return default_join_column
    
    @property
    def counter_join_column(self) -> str:
        default_counter_join_column = f'id_{Model(self.reference).table.name}'
        try:
            return self._counter_join_column or getattr(self.reference, self.mapping)._join_column or default_counter_join_column
        except TypeError:
            return default_counter_join_column

    def setup(self) -> None:
        model = Model(self.owner)
        reference = Model(self.reference)

        join_table = Table(name = self.join_table)
        column = Column(name = self.join_column, auto_increment = False)
        counter_column = Column(name = self.counter_join_column, auto_increment = False)
        
        join_table.add_column(column)
        join_table.add_column(counter_column)

        fk = ForeignKey(column = column, reference = model.table.primary_key.column)
        counter_fk = ForeignKey(column = counter_column, reference = reference.table.primary_key.column)

        join_table.add_foreign_key(fk)
        join_table.add_foreign_key(counter_fk)

        relationship = properties.ToMany(
            reference = reference,
            attribute_name = self.attribute_name,
            strategy = self.load,
            mapping = self.mapping,
            table = model.table,
            join_column = fk,
            secondary_table = join_table,
            secondary_join_column = counter_fk,
        )

        model.add_relationship(relationship)

        if self.master:
            InsertEntityEvent(model).add_listener(PersistAssociationEventListener(relationship)) 


from sideral.mapper import Model
from sideral.mapper import properties
from sideral.schema import Table
from sideral.schema import Column
from sideral.schema import ForeignKey
from sideral.errors import ReferenceNotInstantiated
from sideral.event import InsertEntityEvent, PersistAssociationEventListener