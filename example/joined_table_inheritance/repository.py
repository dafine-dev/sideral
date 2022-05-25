from sideral import repository
import models




@repository(models.Functionary)
class Functionary:
    ...


@repository(models.Supervisor)
class Supervisor:
    ...


@repository(models.Manager)
class Manager:
    ...

