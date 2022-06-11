from __future__ import annotations
from functools import wraps
from .session import transaction
from .session import SessionFactory
from .session import Session



def repository(_class: type):

    def wrapper(cls):

        @wraps(cls, updated = ())
        class Repository(cls):

            def _get_session(self) -> Session:
                return SessionFactory.get()
            
            @transaction
            def select_all(self) -> list[_class]:
                return self._get_session().load(_class)
            
            @transaction
            def select_by_id(self, id: any) -> _class:
                return self._get_session().load(_class, id = id)
            
            @transaction
            def save(self, element: _class) -> _class:
                session = self._get_session()
                session.register_new(element)
                session.flush()
                return session.load(_class, Model(_class).identifier.get_attribute(element))
            
            @transaction
            def save_all(self, elements: list[_class]) -> _class:
                return [self.save(element) for element in elements]
                
            @transaction
            def delete(self, element: _class) -> None:
                session = self._get_session()
                session.register_removed(element)

        return Repository

    
    return wrapper
            


from .mapper import Model
from .event import InsertEntityEvent, PersistAssociationEventListener