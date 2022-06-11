from sideral import repository
import models


@repository(models.Client)
class Client:
    ...

@repository(models.Order)
class Order:
    ...

@repository(models.Student)
class Student:
    ...

@repository(models.Scholarship)
class Scholarship:
    ...

@repository(models.Employee)
class Employee:
    ...

@repository(models.Book)
class Book:
    ...

@repository(models.Author)
class Author:
    ...

@repository(models.Account)
class Account:
    ...

@repository(models.Functionary)
class Functionary:
    ...

@repository(models.Coordinator)
class Coordinator:
    ...

@repository(models.Manager)
class Manager:
    ...

@repository(models.Person)
class Person:
    ...

@repository(models.LegalPerson)
class LegalPerson:
    ...

@repository(models.NaturalPerson)
class NaturalPerson:
    ...

@repository(models.User)
class User:
    ...