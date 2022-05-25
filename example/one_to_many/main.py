from models import Client, Order
import repository

def main():
    client1 = Client(id = 1, name = 'Earl Wilderman')
    client2 = Client(id = 2, name = 'Doreen Thompson')

    order1 = Order(id = 4, value = 194.12)
    order2 = Order(id = 5, value = 215.48)
    order3 = Order(id = 6, value = 487.65)

    client_repository = repository.Client()
    order_repository = repository.Order()

    client1, client2 = client_repository.save_all([client1, client2])
    order1.client = client1
    order2.client = client2
    order3.client = client2

    order1, order2, order3 = order_repository.save_all([order1, order2, order3])


if __name__ == '__main__':
    main()