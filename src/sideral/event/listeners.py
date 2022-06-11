from __future__ import annotations
from sideral.utils import interface, abstract


@interface
class EventListener:
    
    def __call__(self, *args, **kwds) -> None:
        raise NotImplementedError


class PersistAssociationEventListener(EventListener):

    def __init__(self, relationship: Relationship) -> None:
        self._relationship = relationship

    def __call__(self, model: Model, element: object) -> None:
        command = AssociationPersistCommand(model = model, relationship = self._relationship, element = element)
        SessionFactory.get().queue(command)


from sideral.mapper import Model
from sideral.mapper import Relationship
from sideral.command import AssociationPersistCommand
from sideral.session import SessionFactory