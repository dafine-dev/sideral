from __future__ import annotations
from sideral import id, column, one_to_many, many_to_one, join, entity


@entity
class Client:

    def __init__(self, id: int = ..., name: str = ..., orders: list[Order] = ...) -> None:
        self._id = id
        self._name = name
        self._orders = [] if orders is ... else orders
    
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

    @one_to_many(mapping = 'client')
    def orders(self) -> list[Order]:
        return self._orders

    @orders.setter
    def orders(self, orders: list[Order]) -> None:
        self._order = orders

    
@entity(name = 'Orders')
class Order:

    def __init__(self, id: int = ..., value: float = ..., client: Client = None) -> None:
        self._id = id
        self._value = value
        self._client = client
    
    @id
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, id: int) -> None:
        self._id = id
    
    @column
    def value(self) -> float:
        return self._value
    
    @value.setter
    def value(self, value: float) -> None:
        self._value = value
    
    @join(column_name = 'id_client')
    @many_to_one(mapping = 'orders', master = True)
    def client(self) -> Client:
        return self._client

    @client.setter
    def client(self, client: Client) -> None:
        self._client = client