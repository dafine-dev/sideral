from __future__ import annotations
from .test_info import test_info
from sideral import entity
from sideral import id
from sideral import column
from sideral import one_to_one
from sideral import load


@entity
class Student:

    __test_schema__ = ['id', 'name']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'name', strategy = load.EAGER, column = 'name')
    ]

    __test_relationships__ = [
        test_info(attribute_name = 'scholarship', strategy = load.LAZY, mapping = 'student', reference = 'Scholarship', column = 'id_Student', type = 'OneToOne'),
    ]
    
    def __init__(self, id: int = ..., name: str = ..., scholarship: Scholarship = ...) -> None:
        self._id = id
        self._name = name
        self._scholarship = scholarship
    
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

    @one_to_one(mapping = 'student', master = True)
    def scholarship(self) -> Scholarship:
        return self._scholarship
    
    @scholarship.setter
    def scholarship(self, scholarship: Scholarship) -> None:
        self._scholarship = scholarship


@entity
class Scholarship:

    __test_schema__ = ['id', 'percentage', 'id_Student']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'percentage', strategy = load.EAGER, column = 'percentage'),
    ]

    __test_relationships__ = [
        test_info(
            attribute_name = 'student', 
            strategy = load.LAZY, 
            column = 'id_Student', 
            mapping = 'scholarship', 
            reference = 'Student', 
            type = 'ManyToOne'
        ),
    ]

    def __init__(self, id: int = ..., percentage: float = ..., student: Student = ...) -> None:
        self._id = id
        self._percentage = percentage
        self._student = student

    @id
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, id: int) -> None:
        self._id = id
    
    @column
    def percentage(self) -> float:
        return self._percentage
    
    @percentage.setter
    def percentage(self, percentage: float) -> None:
        self._percentage = percentage
    
    @one_to_one(mapping = 'scholarship', owner = True)
    def student(self) -> Student:
        return self._student
    
    @student.setter
    def student(self, student: Student) -> None:
        self._student = student