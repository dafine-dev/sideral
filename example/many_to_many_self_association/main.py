from models import Account
import repository


def main():
    
    account_repository = repository.Account()
    
    account1 = Account(username = 'nicholas_haag')
    account2 = Account(username = 'ryan_bashirian')
    account3 = Account(username = 'priscilla_ritchie')

    account1, account2, account3 = account_repository.save_all([account1, account2, account3])

    account1.followers.append(account2)
    account1.followers.append(account3)
    account2.followers.append(account1)

    account_repository.save_all([account1, account2, account3])


if __name__ == '__main__':
    main()