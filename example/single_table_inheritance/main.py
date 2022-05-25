from models import NaturalPerson, LegalPerson
import repository


def main():
    person1 = NaturalPerson(name = 'Timothy Cummings', nprm = 5487126)
    person2 = LegalPerson(name = "O'Keefe - Langosh", lprm = 9712648)

    natural_person_repository = repository.NaturalPerson()
    legal_person_repository = repository.LegalPerson()

    person1 = natural_person_repository.save(person1)
    person2 = legal_person_repository.save(person2)
    

if __name__ == '__main__':
    main()