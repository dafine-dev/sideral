import pytest
from sideral import mapper
from models import *

__all__ = [
    User,
    Person,
    LegalPerson,
    NaturalPerson,
    Student,
    Scholarship,
    Employee,
    Client,
    Order,
    Book,
    Author,
    Account,
    Functionary,
    Coordinator,
    Manager
]


@pytest.fixture(params = __all__)
def _class(request):
    return request.param


@pytest.fixture
def table_name(_class):
    try:
        return _class.__tablename__
    except AttributeError:
        return _class.__name__

@pytest.fixture
def model(_class):
    return mapper.Model.get(_class)


@pytest.fixture
def columns(_class):
    return _class.__test_columns__


@pytest.fixture
def relationships(_class):
    return _class.__test_relationships__


@pytest.fixture
def schema(_class):
    return _class.__test_schema__


@pytest.fixture(params = [LegalPerson, NaturalPerson, Coordinator, Manager])
def subclass(request):
    return request.param


@pytest.fixture
def submodel(subclass):
    return mapper.Model.get(subclass)


def _get_base_columns(baseclass):
    columns = baseclass.__test_columns__
    try:
        columns = _get_base_columns(baseclass.__bases__[0]) + columns
    except AttributeError:
        return columns

    return columns


@pytest.fixture
def columns_with_base(subclass):
    return _get_base_columns(subclass.__bases__[0]) + subclass.__test_columns__
