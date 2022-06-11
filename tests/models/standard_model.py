from __future__ import annotations
from .test_info import test_info
from sideral import entity
from sideral import id
from sideral import column
from sideral import load


@entity
class User:

    __test_schema__ = ['id_user', 'email']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id_user'),
        test_info(attribute_name = 'email', strategy = load.EAGER, column = 'email')
    ]

    __test_relationships__ = []

    def __init__(self, id: int = ..., email: str = ...) -> None:
        self._id = id
        self._email = email

    @id(name = 'id_user')
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id: int) -> None:
        self._id = id

    @column
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str) -> None:
        self._email = email
