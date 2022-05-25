from __future__ import annotations
from sideral import entity, one_to_one, column, id, join


@entity
class Functionary:

    def __init__(self, id: int = ..., name: str = ..., supervisor: Functionary = ..., supervisee: Functionary = ...) -> None:
        self._id = id
        self._name = name
        self._supervisor = supervisor
        self._supervisee = supervisee

    @id
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, id: int) -> None:
        self._id = id

    @column
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @join(column_name = 'id_supervisor')
    @one_to_one(mapping = 'supervisee', master = True, owner = True)
    def supervisor(self) -> Functionary:
        return self._supervisor

    @supervisor.setter
    def supervisor(self, supervisor: Functionary) -> None:
        self._supervisor = supervisor

    @one_to_one(mapping = 'supervisor')
    def supervisee(self) -> Functionary:
        return self._supervisee
    
    @supervisee.setter
    def supervisee(self, supervisee: Functionary) -> None:
        self._supervisee = supervisee