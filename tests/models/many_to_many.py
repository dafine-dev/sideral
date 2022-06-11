from __future__ import annotations
from .test_info import test_info
from sideral import entity
from sideral import id
from sideral import column
from sideral import join
from sideral import counter_join
from sideral import join_table
from sideral import many_to_many
from sideral import load


@entity
class Book:

    __test_schema__ = ['id', 'title']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'title', strategy = load.EAGER, column = 'title'),
    ]

    __test_relationships__ = [
        test_info(
            attribute_name = 'authors',
            strategy = load.EAGER,
            mapping = 'books',
            column = 'id_book',
            second_column = 'id_author',
            second_table = 'Book_Author',
            type = 'ToMany',
            reference = 'Author'
        )
    ]

    def __init__(self, id: int, title: str, authors: list[Author] = ...) -> None:
        self._id = id
        self._title = title
        self._authors = [] if authors is ... else authors

    @id
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id: int) -> None:
        self._id = id

    @column
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str) -> str:
        self._title = title

    @counter_join(column_name = 'id_author')
    @join(column_name = 'id_book')
    @join_table(name = 'Book_Author')
    @many_to_many(mapping = 'books', master = True, load = load.EAGER)
    def authors(self) -> list[Author]:
        return self._authors

    @authors.setter
    def authors(self, authors: list[Author]) -> None:
        self._authors = authors


@entity
class Author:

    __test_schema__ = ['id', 'name']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'name', strategy = load.EAGER, column = 'name'),
    ]

    __test_relationships__ = [
        test_info(
            attribute_name = 'books',
            strategy = load.LAZY,
            mapping = 'authors',
            column = 'id_author',
            second_column = 'id_book',
            second_table = 'Book_Author',
            type = 'ToMany',
            reference = 'Book'
        )
    ]

    def __init__(self, id: int, name: str, books: list[Book] = ...) -> None:
        self._id = id
        self._name = name
        self._books = [] if books is ... else books

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

    @many_to_many(mapping = 'authors')
    def books(self) -> list[Book]:
        return self._books
    
    @books.setter
    def books(self, books: list[Book]) -> None:
        self._books = books