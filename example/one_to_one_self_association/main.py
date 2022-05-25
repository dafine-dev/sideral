from models import Functionary
import repository


def main():
    functionary_repository = repository.Functionary()

    functionary1 = Functionary(id = 30, name = 'Ramon Champlin')
    functionary2 = Functionary(id = 31, name = 'Lester Senger')
    functionary3 = Functionary(id = 33, name = 'Ernest Baumbach')

    functionary1, functionary2, functionary3 = functionary_repository.save_all([functionary1, functionary2, functionary3])

    functionary1.supervisor = functionary2
    functionary3.supervisor = functionary1
    
    functionary1 = functionary_repository.save(functionary1)
    functionary3 = functionary_repository.save(functionary3)



if __name__ == '__main__':
    main()