from __future__ import annotations
from .test_info import test_info
from sideral import entity
from sideral import id
from sideral import column
from sideral import inheritance
from sideral import strategy
from sideral import subclass
from sideral import discriminator
from sideral import load


@discriminator(name = 'person_type')
@entity
@inheritance(type = strategy.SINGLE_TABLE)
class Person:

    __tablename__ = 'Person'

    __test_schema__ = ['id' , 'name', 'nprn', 'lprn', 'person_type']
    
    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'name', strategy = load.EAGER, column = 'name'),
    ]

    __test_relationships__ = []

    def __init__(self, id: int = ..., name: str = ...) -> None:
        self._id = id
        self._name = name
    
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


@discriminator(value = 1)
@subclass
class NaturalPerson(Person):

    __test_columns__ = [
        test_info(attribute_name = 'nprn', strategy = load.EAGER, column = 'nprn'),
    ]

    __test_relationships__ = []


    def __init__(self, id: int = ..., name: str = ..., nprn: int = ...) -> None:
        super().__init__(id, name)
        self._nprn = nprn
    
    @column
    def nprn(self) -> int: # natural person registry number
        return self._nprn
    
    @nprn.setter
    def nprn(self, nprn: int) -> None:
        self._nprn = nprn


@discriminator(value = 2)
@subclass
class LegalPerson(Person):

    __test_columns__ = [
        test_info(attribute_name = 'lprn', strategy = load.EAGER, column = 'lprn'),
    ]

    __test_relationships__ = []
    
    def __init__(self, id: int = ..., name: str = ..., lprn: int = ...) -> None:
        super().__init__(id, name)
        self._lprn = lprn
     
    @column
    def lprn(self) -> int: # legal person registry number
        return self._lprn
    
    @lprn.setter
    def lprn(self, lprn: int) -> None:
        self._lprn = lprn