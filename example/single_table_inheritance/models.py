from __future__ import annotations
from sideral import entity, id, column, inheritance, strategy, subclass, discriminator


@discriminator(name = 'person_type')
@entity
@inheritance(type = strategy.SINGLE_TABLE)
class Person:

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

    def __init__(self, id: int = ..., name: str = ..., nprm: int = ...) -> None:
        super().__init__(id, name)
        self._nprm = nprm
    
    #Natural Person Register Number
    @column
    def nprm(self) -> int:
        return self._nprm

    @nprm.setter
    def nprm(self, nprm: int) -> None:
        self._nprm = nprm


@discriminator(value = 2)
@subclass
class LegalPerson(Person):

    def __init__(self, id: int = ..., name: str = ..., lprm: int = ...) -> None:
        super().__init__(id, name)
        self._lprm = lprm

    #Legal Person Register Number
    @column
    def lprm(self) -> int:
        return self._lprm
    
    @lprm.setter
    def lprm(self, lprm: int) -> None:
        self._lprm = lprm
