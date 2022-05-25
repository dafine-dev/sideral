import repository
from models import Author, Book


def main():
    author1 = Author(id = 1, name = 'Erich Gamma')
    author2 = Author(id = 2, name = 'Richard Helm')
    author3 = Author(id = 3, name = 'Ralph Johnson')
    author4 = Author(id = 4, name = 'John Vlissides')
    author5 = Author(id = 5, name = 'Jose Saramago')

    book1 = Book(id = 1, title = 'Design Patterns: Elements of reusable object-oriented software')
    book2 = Book(id = 2, title = 'O homem duplicado')

    book_repository = repository.Book()
    author_repository = repository.Author()

    author1, author2, author3, author4, author5 = author_repository.save_all([author1, author2, author3, author4, author5])
    book1.authors = [author1, author2, author3, author4]
    book2.authors = [author5]
    
    book1 = book_repository.save(book1)
    book2 = book_repository.save(book2)

    book1.authors.pop(1)

    book1 = book_repository.save(book1)
    

if __name__ == '__main__':
    main()