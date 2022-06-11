from __future__ import annotations
from typing import TYPE_CHECKING, ParamSpec, TypeVar
from mysql import connector
from collections.abc import Callable
from .utils import abstract, ordered_set
from functools import wraps, partial


if TYPE_CHECKING:
    from .query import Query
    from .proxy import Proxy
    from .command import Command


class Session:
    _last_id: any
    _queue: ordered_set[Command]
    _result: ResultSet

    def __init__(self) -> None:
        self._queue = ordered_set()
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
        self._queue.add(
            EntityInsertCommand(
                model = Model.get(element.__class__),
                element = element
            )
        )
        
    def register_dirty(self, element: object) -> None:
        self._queue.add(
            EntityUpdateCommand(
                model = Model.get(element.__class__),
                element = element
            )
        )
    
    def register_removed(self, element: object) -> None:
        self._queue.add(
            EntityDeleteCommand(
                model = Model.get(element.__class__),
                element = element
            )
        )
    
    def load(self, _class: type, id: any = ...) -> Proxy | list[Proxy]:
        loader = Loader(model = Model(_class))
        response = loader.load() if id is ... else loader.load_by_id(id)
        return response
    
    def remove(self, element: object) -> None:
        self._queue.remove(element)

    def clear(self) -> None:
        self._queue = ordered_set()

    def flush(self) -> None:
        for command in self._queue:
            command.execute()
        
        self.clear()
    
    def queue(self, command: Command) -> None:
        self._queue.add(command)

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
        print(query)
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


# def transaction(function: Callable[_params, _return] = None, isolated: bool = False) -> Callable[_params, _return]:

#     if function is None:
#         return partial(transaction, isolated = isolated)

#     @wraps(function)
#     def isolated_transaction(*args: _params.args, **kwargs: _params.kwargs) -> _return:
#         previous_session = SessionFactory.get()
#         breakpoint()
        
#         response = ...
#         with SessionFactory.start() as session:
#             response = function(*args, **kwargs)
        
#         session.flush()
#         session.transaction.commit()
#         session.close()
#         SessionFactory.restore(previous_session)
#         return response

#     @wraps(function)
#     def joined_transaction(*args: _params.args, **kwargs: _params.kwargs) -> _return:
#         session = SessionFactory.get()
        
#         nonlocal isolated_transaction

#         if session is None:
#             return isolated_transaction(*args, **kwargs)
#         else:
#             response = ...
#             with SessionFactory.get() as session:
#                 response = function(*args, **kwargs)
#             return response

#     return isolated_transaction if isolated else joined_transaction 


# def transaction(fn = None, isolated: bool = False):

#     def wrapper(*args, **kwargs):
#         session = SessionFactory.get()

#         if session is None:
#             reponse = ...
#             with SessionFactory.start() as session:
#                 response = fn(*args, **kwargs)
#             session.flush()
#             session.transaction.commit()
#             session.close()
#             SessionFactory.restore(session)
        
#         else:
#             if isolated is True:
#                 response = SessionFactory.start()
#         ...
    
#     return wrapper


def _isolated_transaction(fn):

    def wrapper(*args, **kwargs):
        previous_session = SessionFactory.get()
        response = None
        
        with SessionFactory.start() as session:
            response = fn(*args, **kwargs)
        
        session.flush()
        session.transaction.commit()
        session.close()
        SessionFactory.restore(previous_session)
        return response
    
    return wrapper


def transaction(fn = None, isolated: bool = True):

    if fn is None:
        return partial(transaction, isolated = isolated)
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        session = SessionFactory.get()

        if isolated or session is None:
            return _isolated_transaction(fn)(*args, **kwargs)
        else:
            response = None
            with SessionFactory.get():
                response = fn(*args, **kwargs)
            return response

    return wrapper


from .result import ResultSet
from .mapper import Model
from .loader import Loader
from .command import EntityUpdateCommand, EntityDeleteCommand, EntityInsertCommand