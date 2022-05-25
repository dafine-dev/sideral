from sideral import repository
import models


@repository(models.Client)
class Client:
    ...

@repository(models.Order)
class Order:
    ...