from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .mapper import Model, Relationship



class Persister:
    _session: Session
    _model: Model

    def __init__(self, model: Model) -> None:
        self._model = model
        self._session = SessionFactory.get()
    
    def build_insert(self, element: object) -> Insert:
        return (
            self._model.build_insert()
            .values((column.column, column.get_attribute(element)) for column in self._model.columns(with_base = False))
        )
    
    def build_update(self, element: object) -> Update:
        primary_key = self._model.table.primary_key.column
        return (
            self._model.build_update()
            .set((column.column, column.get_attribute(element)) for column in self._model.columns(with_base = False))
            .where(primary_key == self._model.identifier.get_attribute(element))
        )
    
    def build_delete(self, element: object) -> Delete:
        primary_key = self._model.table.primary_key.column
        return (
            self._model.build_delete()
            .where(primary_key == self._model.identifier.get_attribute(element))
        )
    
    def insert(self, element: object) -> None:
        self._session.transaction.execute_query(self.build_insert(element))
        id_value = self._session.get_last_id()

        if id_value is not None:
            setattr(element, self._model.identifier.attribute_name, id_value)

        for relationship in self._model.relationships(with_base = False):
            if relationship.master:
                AssociationPersister(relationship, self._model).persist(element)

        return id_value
    
    def update(self, element: object) -> None:
        self._session.transaction.execute_query(self.build_update(element))

        for relationship in self._model.relationships(with_base = False):
            if relationship.master:
                AssociationPersister(relationship, self._model).persist(element)
    
    def delete(self, element: object) -> None:
        self._session.transaction.execute_query(self.build_delete(element))



class JoinedTablePersister(Persister):

    def build_insert(self, element: object) -> Insert:
        primary_key = self._model.table.primary_key.column
        return super().build_insert(element).values([(primary_key, self._model.identifier.get_attribute(element))])

    def insert(self, element: object) -> None:
        self._model.base.persister.insert(element)
        super().insert(element)
    
    def update(self, element: object) -> None:
        self._model.base.persister.update(element)
        return super().update(element)

    def delete(self, element: object) -> None:
        super().delete(element)
        self._model.base.persister.delete(element)



class SingleTablePersister(Persister):
    
    def build_insert(self, element: object) -> Insert:
        return self._model.build_insert() \
                          .values((column.column, column.get_attribute(element)) for column in self._model.columns())



class AssociationPersister:

    def __init__(self, relationship: Relationship, model: Model) -> None:
        self._model = model
        self._relationship = relationship
        self._session = SessionFactory.get()
    
    def build_insert(self, pk_value: any, key_value: any) -> Insert:
        join_column = self._relationship.join_column.column
        table = join_column.table
        key_column = self._relationship.relative_key_column
        return (
            Insert()
            .into(table)
            .values([(join_column, pk_value), (key_column, key_value)])
            .on_duplicate_key()
        )
    
    def build_update(self, pk_value: any, key_value: any) -> None:
        join_column = self._relationship.join_column.column
        table = join_column.table
        key_column = self._relationship.relative_key_column
        return (
            Update()
            .table(table)
            .set([(join_column, key_value)])
            .where(key_column == pk_value)
        )
    
    def build_delete(self, pk_value: any, key_value: any) -> None:
        join_column = self._relationship.join_column.column
        table = join_column.table
        key_column = self._relationship.relative_key_column
        #add criteria class later
        return (
            Delete()
            .from_(table)
            .where(join_column == pk_value, key_column == key_value)
        )

    def insert(self, pk_value: any, element: object) -> None:
        key_value = self._relationship.reference.identifier.get_attribute(element)
        sql = self.build_insert(pk_value, key_value) if self._relationship.is_many_to_many else self.build_update(pk_value, key_value)    
        self._session.transaction.execute_query(sql)
    
    def delete(self, pk_value: any, element: object) -> None:
        key_value = self._relationship.reference.identifier.get_attribute(element)
        sql = self.build_delete(pk_value, key_value) if self._relationship.is_many_to_many else self.build_update(pk_value, None)
        self._session.transaction.execute_query(sql)

    def persist(self, element: object) -> None:
        elements = self._relationship.get_attribute(element)

        if not hasattr(elements, '__iter__'):
            elements = set() if elements in (None, ...) else set([elements])
        else:
            elements = set(elements)

        pk_value = self._model.identifier.get_attribute(element)

        self._session.clear_result()
        
        self._session.transaction.execute_query(self._relationship.build_select(id = pk_value))
        
        persisted_elements = set(self._relationship._post_execute_action(self._session.get_result()))

        for element in elements.difference(persisted_elements):
            self.insert(pk_value, element)

        for element in persisted_elements.difference(elements):
            self.delete(pk_value, element)         

    @property
    def is_many_to_many(self) -> bool:
        if self._relationship.secondary_table:
            return True
        else:
            return False




from .query import Insert, Update, Delete
from .session import Session, SessionFactory