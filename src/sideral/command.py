from __future__ import annotations
from .utils import interface

@interface
class Command:
    
    def execute(self) -> None:
        ...

class EntityPersistCommand(Command):
    _model: Model
    _element: _model._class

    def __init__(self, model: Model, element: _model._class) -> None:
        self._model = model
        self._element = element
    
    def __hash__(self) -> int:
        return hash(self._element)


class EntityDeleteCommand(EntityPersistCommand):
    
    def execute(self) -> None:
        self._model.persister.delete(self._element)
        DeleteEntityEvent(self._model).post_event(element = self._element)


class EntityUpdateCommand(EntityPersistCommand):
    
    def execute(self) -> None:
        self._model.persister.update(self._element)
        UpdateEntityEvent(self._model).post_event(element = self._element)


class EntityInsertCommand(EntityPersistCommand):
    
    def execute(self) -> None:
        self._model.persister.insert(self._element)
        InsertEntityEvent(self._model).post_event(element = self._element)


class AssociationPersistCommand(Command):
    _model: Model
    _relationship: Relationship
    _element: _model._class
    
    def __init__(self, model: Model, relationship: Relationship, element: _model._class) -> None:
        self._model = model
        self._relationship = relationship
        self._element = element

    def execute(self) -> None:
        persister = AssociationPersister(
            relationship = self._relationship,
            model = self._model
        )
        association_list = self._relationship.get_attribute(self._element)
        key = self._model.identifier.get_attribute(self._element)
        persister.persist(association_list, key)


from .mapper import Model
from .mapper import Relationship
from .persister import AssociationPersister
from .event import InsertEntityEvent, UpdateEntityEvent, DeleteEntityEvent