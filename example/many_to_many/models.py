from __future__ import annotations
from sideral import id, column, many_to_many, join_table, entity, join, counter_join,  load


@entity
class Book:

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
    @many_to_many(mapping = 'books', master = True, load =  load.EAGER)
    def authors(self) -> list[Author]:
        return self._authors

    @authors.setter
    def authors(self, authors: list[Author]) -> None:
        self._authors = authors

@entity
class Author:

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