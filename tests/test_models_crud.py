import pytest
import repository
from models import User 
from models import LegalPerson, NaturalPerson
from models import Functionary, Coordinator, Manager
from sideral.errors import SideralException


user = User(email = 'brooks.kshlerin81@hotmail.com')

persons = [
    LegalPerson(name = 'Quigley LLC', lprn = 5872487),
    NaturalPerson(name = 'Roxanne Terry', nprn = 3548473),
]

functionaries = [
    Functionary(name = 'Jan Deckow'),
    Coordinator(name = 'Grace Stroman', sector = 'sales'),
    Manager(name = 'Sylvester Hirthe', sector = 'support', unit = 'Jakobmouth'),
]


@pytest.mark.parametrize('obj, class_repository', [
    (user, repository.User()),
    (persons[0], repository.LegalPerson()),
    (persons[1], repository.NaturalPerson()),
    (functionaries[0], repository.Functionary()),
    (functionaries[1], repository.Coordinator()),
    (functionaries[2], repository.Manager()), 
])
def test_insert(obj, class_repository):
    persisted_obj = class_repository.save(obj)
    obj.id = persisted_obj.id
    assert persisted_obj == obj


@pytest.mark.parametrize('id, class_repository, expected_response', [
    (1, repository.User(), user),
    (1, repository.Person(), persons[0]),
    (2, repository.Person(), persons[1]),
    (1, repository.LegalPerson(), persons[0]),
    (2, repository.NaturalPerson(), persons[1]),
    (1, repository.Functionary(), functionaries[0]),
    (2, repository.Functionary(), functionaries[1]),
    (3, repository.Functionary(), functionaries[2]),
    (2, repository.Coordinator(), functionaries[1]),
    (3, repository.Coordinator(), functionaries[2]),
    (3, repository.Manager(), functionaries[2]),
])
def test_select(id, class_repository, expected_response):
    assert class_repository.select_by_id(id) == expected_response


@pytest.mark.parametrize('id, class_repository, changes', [
    (1, repository.User(), [('email', 'brooks.kshlerin@gmail.com')]),
    (1, repository.LegalPerson(), [('name', 'Moore - Morissette'), ('lprn', 587248710)]),
    (2, repository.NaturalPerson(), [('name', 'Roxanne Terry Klocko'), ('nprn', 354847354)]),
    (1, repository.Functionary(), [('name', 'Jan Deckow Hessel')]),
    (2, repository.Coordinator(), [('name', 'Grace Stroman Runolfsson'), ('sector', 'finance')]),
    (3, repository.Manager(), [('name', 'Sylvester Hirthe Satterfield'), ('sector', 'sales'), ('unit', 'Raybury')]),
])
def test_update(id, class_repository, changes):
    obj = class_repository.select_by_id(id)
    
    for attribute, value in changes: 
        setattr(obj, attribute, value)

    persisted_obj = class_repository.save(obj)
    
    assert obj == persisted_obj


@pytest.mark.parametrize('id, class_repository', [
    (1, repository.User()),
    (1, repository.LegalPerson()),
    (2, repository.NaturalPerson()),
    (1, repository.Functionary()),
    (2, repository.Coordinator()),
    (3, repository.Manager()),
])
def test_delete(id, class_repository):
    obj = class_repository.select_by_id(id)
    class_repository.delete(obj)
    with pytest.raises(SideralException):
        class_repository.select_by_id(id)