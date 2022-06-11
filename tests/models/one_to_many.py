from __future__ import annotations
from .test_info import test_info
from sideral import entity
from sideral import id
from sideral import column
from sideral import one_to_many
from sideral import many_to_one
from sideral import load


@entity
class Client:

    __test_schema__ = ['id', 'name']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'name', strategy = load.EAGER, column = 'name'),
    ]

    __test_relationships__ = [
        test_info(
            attribute_name = 'orders',
            strategy = load.LAZY,
            column = 'id_Client',
            second_column = None,
            second_table = None,
            mapping = 'client',
            reference = 'Order',
            type = 'ToMany'
        ),
    ]

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
        self._orders = orders



@entity(name = 'Orders')
class Order:

    __tablename__ = 'Orders'

    __test_schema__ = ['id', 'value', 'id_Client']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'value', strategy = load.EAGER, column = 'value'),
    ]

    __test_relationships__ = [
        test_info(
            attribute_name = 'client',
            strategy = load.LAZY,
            column = 'id_Client',
            mapping = 'orders',
            reference = 'Client',
            type = 'ManyToOne',
        ),
    ]
    
    def __init__(self, id: int = ..., value: float = ..., client: Client = ...) -> None:
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
    
    @many_to_one(mapping = 'orders', master = True)
    def client(self) -> Client:
        return self._client
    
    @client.setter
    def client(self, client: Client) -> None:
        self._client = client