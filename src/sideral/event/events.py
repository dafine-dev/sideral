from __future__ import annotations
from sideral.utils import abstract


class Event:
    _listeners: list[EventListener]

    def add_listener(self, listener: EventListener) -> None:
        self._listeners.append(listener)

    def post_event(self, *args, **kwargs) -> None:
        for listener in self._listeners:
            listener(*args, **kwargs)

@abstract
class EntityEvent(Event):
    _instances: dict[str, EntityEvent]

    def __new__(cls, model: Model) -> EntityEvent:
        name = model._class.__name__
        if name in cls._instances:
            return cls._instances[name]
        else:
            event = object.__new__(cls)
            event.init(model)
            cls._instances[name] = event
            return event
        
    def init(self, model: Model) -> None:
        self._model = model
        self._listeners = []
    
    def post_event(self, element: object) -> None:
        for listener in self._listeners:
            listener(model = self._model, element = element)


class UpdateEntityEvent(EntityEvent):
    _instances: dict[str, EntityEvent] = {}

class InsertEntityEvent(EntityEvent):
    _instances: dict[str, EntityEvent] = {}

class DeleteEntityEvent(EntityEvent):
    _instances: dict[str, EntityEvent] = {}


from .listeners import EventListener
from sideral.mapper import Model