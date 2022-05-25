import models
from sideral import repository

@repository(models.Person)
class Person:
    ...


@repository(models.NaturalPerson)
class NaturalPerson:
    ...


@repository(models.LegalPerson)
class LegalPerson:
    ...