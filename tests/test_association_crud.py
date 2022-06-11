from __future__ import annotations
from models import Author, Book, Account, Order, Client, Scholarship, Student, Employee
import pytest
import repository

authors = [
    Author(id = 1, name = 'Erich Gamma'),
    Author(id = 2, name = 'Richard Helm'),
    Author(id = 3, name = 'Ralph Johnson'),
    Author(id = 4, name = 'John Vlissides'),
    Author(id = 5, name = 'Jose Saramago')
]

books = [
    Book(id = 1, title = 'Design Patterns: Elements of reusable object-oriented software'),
    Book(id = 2, title = 'O homem duplicado'),
    Book(id = 3, title = 'Ensaio sobre a cegueira')
]

accounts = [
    Account(id = 1, username = 'evelyn_adams'),
    Account(id = 2, username = 'ronald_grady'),
    Account(id = 3, username = 'henrietta_romaguera'),
    Account(id = 4, username = 'nikolaus'),
    Account(id = 5, username = 'veronicamayer')
]


scholarships = [
    Scholarship(percentage = 45.7),
    Scholarship(percentage = 75.8)
]

students = [
    Student(name = 'Irving Daniel')
]

clients = [
    Client(name = 'Moses Nienow'),
    Client(name = 'Cathy Kuhlman')
]

orders = [
    Order(value = 374.8),
    Order(value = 712.4),
]

employees = [
    Employee(name = 'Felicia McKenzie'),
    Employee(name = 'Eric Kling'),
    Employee(name = 'Lillie Wisozk')
]


parameters = '''
    master_repository,
    associated_repository,
    obj,
    associated_objs,
    property_name,
'''

@pytest.mark.parametrize(parameters,[
    (repository.Order(), repository.Client(), orders[0], clients[0], 'client'),
    (repository.Order(), repository.Client(), orders[1], clients[0], 'client'),
    (repository.Student(), repository.Scholarship(), students[0], scholarships[0], 'scholarship'),
    (repository.Employee(), repository.Employee(), employees[0], employees[1], 'supervisor'),
    (repository.Book(), repository.Author(), books[0], authors[:4], 'authors'),
    (repository.Book(), repository.Author(), books[1], authors[4:], 'authors'),
    (repository.Book(), repository.Author(), books[2], authors[4:], 'authors'),
    (repository.Account(), repository.Account(), accounts[0], accounts[3:], 'followers'),
    (repository.Account(), repository.Account(), accounts[1], accounts[0:4], 'followers')    
])
def test_insert(master_repository, associated_repository, obj, associated_objs, property_name):
    associated_objs = associated_repository.save_all(associated_objs) \
                        if isinstance(associated_objs, list) \
                        else associated_repository.save(associated_objs)
    
    setattr(obj, property_name, associated_objs)

    persisted_obj = master_repository.save(obj)

    assert getattr(obj, property_name) == getattr(persisted_obj, property_name)


parameters = '''
    id,
    class_repository,
    expected_response,
    property_name
'''

@pytest.mark.parametrize(parameters, [
    (1, repository.Order(), clients[0], 'client'),  
    (2, repository.Order(), clients[0], 'client'),
    (1, repository.Client(), orders, 'orders'),
    (1, repository.Student(), scholarships[0], 'scholarship'),  
    (1, repository.Scholarship(), students[0], 'student'),  
    (2, repository.Employee(), employees[1], 'supervisor'),  
    (1, repository.Book(), authors[:4], 'authors'),
    (5, repository.Author(), books[1:], 'books'),
    (1, repository.Account(), accounts[3:], 'followers'),
    (4, repository.Account(), accounts[:2], 'following')
])
def test_select(id, class_repository, expected_response, property_name):
    obj = class_repository.select_by_id(id)
    assert getattr(obj, property_name) == expected_response


parameters = '''
    id,
    objs,
    master_repository,
    associated_repository,
    property_name,
'''

@pytest.mark.parametrize(parameters, [
    (1, clients[1], repository.Order(), repository.Client(), 'client'),
    (1, scholarships[1], repository.Student(), repository.Scholarship(), 'scholarship'),
    (2, employees[2], repository.Employee(), repository.Employee(), 'supervisor'),
    (1, authors[:3], repository.Book(), repository.Author(), 'authors'),
    (1, authors[1:4], repository.Book(), repository.Author(), 'authors'),
    (2, accounts[1:4], repository.Account(), repository.Account(), 'followers'),
    (2, accounts[0:4], repository.Account(), repository.Account(), 'followers'),
])
def test_update(id, objs, master_repository, associated_repository, property_name):
    obj = master_repository.select_by_id(id)
    associated_objs = associated_repository.save_all(objs) \
                        if isinstance(objs, list) \
                        else associated_repository.save(objs)
    
    setattr(obj, property_name, associated_objs)

    persisted_obj = master_repository.save(obj)

    assert getattr(obj, property_name) == getattr(persisted_obj, property_name)



parameters = '''
    id,
    master_repository,
    property_name,
'''

@pytest.mark.parametrize(parameters, [
    (1, repository.Order(), 'client'),
    (1, repository.Student(), 'scholarship'),
    (2, repository.Employee(), 'supervisor'),
    (1, repository.Book(), 'authors'),
    (2, repository.Account(), 'followers')
])
def test_delete(id, master_repository, property_name):
    obj = master_repository.select_by_id(id)
    setattr(obj, property_name, None)

    persisted_obj = master_repository.save(obj)

    assert not getattr(persisted_obj, property_name)