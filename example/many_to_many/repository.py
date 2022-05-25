from sideral import repository
import models


@repository(models.Book)
class Book:
    ...


@repository(models.Author)
class Author:
    ...