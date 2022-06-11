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
            .values((relationship.join_column.column, relationship.get_key(element))
                     for relationship in self._model.relationships(with_base = False) 
                     if relationship.owner
            )
        )
    
    def build_update(self, element: object) -> Update:
        primary_key = self._model.table.primary_key.column
        return (
            self._model.build_update()
            .set((column.column, column.get_attribute(element)) for column in self._model.columns(with_base = False))
            .set((relationship.join_column.column, relationship.get_key(element)) 
                  for relationship in self._model.relationships(with_base = False) 
                  if relationship.owner
            )
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

        return id_value
    
    def update(self, element: object) -> None:
        self._session.transaction.execute_query(self.build_update(element))
    
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
    
    def build_insert(self, key: any) -> Insert:
        join_column = self._relationship.join_column.column
        return Insert() \
                .into(join_column.table) \
                .values([
                   (join_column, key) 
                ]) \
                .on_duplicate_key()

    def build_update(self, key: any) -> Update:
        join_column = self._relationship.join_column.column
        return Update() \
                .table(join_column.table) \
                .set([
                    (join_column, key)
                ])

    def build_delete(self, key: any) -> Delete:
        join_column = self._relationship.join_column.column
        return Delete() \
                .from_(join_column.table) \
                .where(join_column == key)

    def save(self, element: object, key: any) -> None:
        sql = ...
        pk = self._relationship.reference.identifier.get_attribute(element)

        if self._relationship.is_many_to_many:
            column = self._relationship.secondary_join_column.column
            sql = self.build_insert(key) \
                    .values([(column, pk)])
        else:
            column = self._relationship.reference.table.primary_key.column
            sql = self.build_update(key) \
                    .where(column == pk)

        self._session.transaction.execute_query(sql)

    def delete(self, element: object, key: any) -> None:
        sql = ...
        pk = self._relationship.reference.identifier.get_attribute(element)
        
        if self._relationship.is_many_to_many:
            column = self._relationship.secondary_join_column.column
            sql = self.build_delete(key) \
                    .where(column == pk)
        else:
            column = self._relationship.reference.table.primary_key.column
            sql = self.build_update(key) \
                    .where(column == pk)
        
        self._session.transaction.execute_query(sql)
    
    def reset(self, key: any) -> None:
        sql = self.build_delete(key) \
                if self._relationship.is_many_to_many \
                else self.build_update(None).where(self._relationship.join_column.column == key)

        self._session.transaction.execute_query(sql)

    def recreate(self, elements: list[object], key: any) -> None:
        elements = set(elements)
        persisted_elements = self.load_relationship(key)
        
        for element in persisted_elements.difference(elements):
            self.delete(element, key)
        
        for element in elements.difference(persisted_elements):
            self.save(element, key)
    
    def persist(self, elements: list[object], key: any) -> None:
        if elements in (None, ..., []):
            self.reset(key)
        elif not hasattr(elements, '__iter__'):
            self.recreate([elements], key)
        else:
            self.recreate(elements, key)
    
    def load_relationship(self, id: any) -> set:
        self._session.clear_result()
        self._session.transaction.execute_query(self._relationship.build_select(id = id))
        
        return set(self._relationship._post_execute_action(self._session.get_result()))     




from .query import Insert, Update, Delete
from .session import Session, SessionFactory