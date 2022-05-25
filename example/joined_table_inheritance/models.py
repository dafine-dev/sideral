from __future__ import annotations
from sideral import entity, inheritance, strategy, derived_key, id, column, one_to_many, many_to_one,  load

@entity
@inheritance(type = strategy.JOINED_TABLE)
class Functionary:

    def __init__(self, id: int, name: str) -> None:
        self._id = id
        self._name = name
        self._vendas = []
    
    @id
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, value) -> None:
        self._id = value
    
    @column
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value) -> None:
        self._name = value    

    @one_to_many(mapping = 'funcionario', load =  load.EAGER)
    def vendas(self) -> list[Order]:
        return self._vendas 
    
    @vendas.setter
    def vendas(self, vendas: list[Order]) -> None:
        self._vendas = vendas
    
    def __str__(self) -> str:
        return str(self.__dict__)


@derived_key(name = 'id')
@entity
@inheritance(type = strategy.JOINED_TABLE)
class Supervisor(Functionary):

    def __init__(self, id: int, name: str, acesso: int) -> None:
        self._id = id
        self._name = name
        self._acesso = acesso
        self._vendas = []

    @column
    def acesso(self) -> int:
        return self._acesso
    
    @acesso.setter
    def acesso(self, value) -> None:
        self._acesso = value
    

@derived_key(name = 'id')
@entity
class Manager(Supervisor):
    
    @column(load =  load.LAZY)
    def sala(self) -> int:
        return self._sala
    
    @sala.setter
    def sala(self, value) -> None:
        self._sala = value


@entity
class Order:
    
    def __init__(self, id: int, value: float) -> None:
        self._id = id
        self._value = value
    
    @id
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @column
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value
    
    @many_to_one(mapping = 'vendas', master = True)
    def funcionario(self) -> Functionary:
        return self._funcionario

    @funcionario.setter
    def funcionario(self, funcionario: Functionary) -> None:
        self._funcionario = funcionario

    def __str__(self) -> str:
        return str(self.__dict__)


