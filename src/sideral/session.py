from __future__ import annotations
from typing import TYPE_CHECKING, ParamSpec, TypeVar
from mysql import connector
from collections.abc import Callable
from .utils import abstract, ordered_set
from functools import wraps, partial


if TYPE_CHECKING:
    from .query import Query
    from .proxy import Proxy


class Session:

    def __init__(self) -> None:
        self._new = ordered_set()
        self._dirty = ordered_set()
        self._removed = ordered_set()
        self._conn = connector.connect(option_files = 'database.conf', option_groups = ['connection'])
        self._last_id = None
        self._result = ResultSet()
    
    @property
    def transaction(self) -> Transaction:
        try:
            return self._transaction
        except AttributeError:
            self._transaction = Transaction(session = self)
            return self._transaction
    
    def __enter__(self) -> Session:
        return self
    
    def __exit__(self, *exc) -> None:
        ...
    
    def register_new(self, element: object) -> None:
        if element in self._dirty or element in self._removed:
            raise Exception(f"Can't insert {element.__class__.__name__} element that already exist in the database.")
        
        self._new.add(element)
        
    def register_dirty(self, element: object) -> None:
        model = Model.get(element.__class__)
        id = model.identifier.get_attribute(element)

        if id in (None, ..., 0, ''):
            raise Exception(f"Can't update {element.__class__.__name__.lower()} element with unset id.")
        
        self._dirty.add(element)
    
    def register_removed(self, element: object) -> None:
        model = Model.get(element.__class__)
        id = model.identifier.get_attribute(element)

        if id in (None, ..., 0, ''):
            raise Exception(f"Can't delete {element.__class__.__name__.lower()} element with unset id.")
        
        if element in self._dirty:
            self._dirty.remove(element)
        
        self._removed.add(element)
    
    def load(self, _class: type, id: any = ...) -> Proxy | list[Proxy]:
        loader = Loader(model = Model(_class))
        response = loader.load() if id is ... else loader.load_by_id(id)
        return response
    
    def remove(self, element: object) -> None:
        self._new.remove(element)
        self._dirty.remove(element)
        self._removed.remove(element)

    def clear(self) -> None:
        self._new = ordered_set()
        self._dirty = ordered_set()
        self._removed = ordered_set()

    def flush(self) -> None:
        persister = ...
        for element in self._new:
            persister = Model(element.__class__).persister
            persister.insert(element)            
        
        for element in self._dirty:
            persister = Model(element.__class__).persister
            persister.update(element)

        for element in self._removed:
            persister = Model(element.__class__).persister
            persister.delete(element)
        
        self.clear()
        

    def get_result(self) -> ResultSet:
        return self._result
    
    def clear_result(self) -> ResultSet:
        self._last_id = None
        self._result = ResultSet()

    def get_last_id(self) -> any:
        return self._last_id

    def close(self) -> None:
        self.clear()
        self._conn.close()

    
    


class Transaction:

    def __init__(self, session: Session) -> None:
        self._session = session

    def execute_query(self, query: Query, params: dict[str, any] = {}) -> None:
        cursor = self._session._conn.cursor(dictionary = True)
        cursor.execute(query.statement)
        if cursor.lastrowid:
            self._session._last_id = cursor.lastrowid
        else:
            data = cursor.fetchall()
            if len(data) == 1 and (all(value in (None, ...) for value in data[0].values())):
                data = []
            
            self._session._result.add_data(data)
        
        cursor.close()

    def commit(self) -> None:
        self._result = ResultSet()
        self._session._conn.commit()
    


@abstract
class SessionFactory:

    _context_session: Session = None

    @classmethod
    def start(self) -> Session:
        self._context_session = Session()
        return self._context_session
    
    @classmethod
    def get(cls) -> Session:
        return cls._context_session

    @classmethod
    def restore(self, session: Session) -> Session:
        self._context_session = session


_params = ParamSpec('_params')
_return = TypeVar('_return')


def transaction(function: Callable[_params, _return] = None, isolated: bool = False) -> Callable[_params, _return]:

    if function is None:
        return partial(transaction, isolated = isolated)

    @wraps(function)
    def isolated_transaction(*args: _params.args, **kwargs: _params.kwargs) -> _return:
        previous_session = SessionFactory.get()
        
        response = ...
        with SessionFactory.start() as session:
            response = function(*args, **kwargs)
        
        session.flush()
        session.transaction.commit()
        session.close()
        SessionFactory.restore(previous_session)
        return response

    @wraps(function)
    def joined_transaction(*args: _params.args, **kwargs: _params.kwargs) -> _return:
        session = SessionFactory.get()
        
        if session is None:
            return isolated_transaction(*args, **kwargs)
        else:
            response = ...
            with SessionFactory.get() as session:
                response = function(*args, **kwargs)
            return response

    return isolated_transaction if isolated else joined_transaction            


from .result import ResultSet
from .mapper import Model
from .loader import Loader