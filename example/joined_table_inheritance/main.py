import repository
from models import Functionary, Supervisor, Manager



def main():
    functionary = Functionary(id = None, name = 'Jerald Lind')
    supervisor = Supervisor(id = None, name = 'Mario Mante')
    
    functionary_repository = repository.Functionary()
    supervisor_repository = repository.Supervisor()

    functionary_repository.save(functionary)
    supervisor_repository.save(supervisor)


if __name__ == 'main':
    main()