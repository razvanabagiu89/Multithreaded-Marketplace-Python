"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import threading


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    # genereaza cate un id pt fiecare producer care cheama register_producer()
    producer_ids: int
    # nested dict de tipul
    # { "producer_id" : { "product_id" : qty } }
    queue: dict

    # nested dict de tipul
    # { "cart_id" : [] } unde [] -> lista cu obiectele din cart
    carts: dict
    cart_ids : int

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.producer_ids = 0
        self.queue = {}
        self.carts = {}
        self.cart_ids = 0

        self.lock = threading.Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        producer_id = self.producer_ids
        self.producer_ids += 1
        return producer_id


    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        # producer_id e pentru prima oara, trebuie creata o intrare pt el
        if producer_id not in self.queue:
            self.queue[producer_id] = dict()
        else:
            # products este dictionarul de tip { "product_id" : qty}
            products = self.queue[producer_id]
            # verifica daca nu si a depasit limita prin insumarea de qty
            current_size = sum(products.values())
            # daca inca are loc
            if current_size < self.queue_size_per_producer:
                # verifica daca nu exista produsul curent si il adauga cu qty 1
                if product not in products:
                    products[product] = 1  # product este product_id si 1 este qty
                # daca exista deja doar mareste qty
                else:
                    products[product] += 1
                return True
            return False
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        cart_id = self.cart_ids
        self.carts[cart_id] = list()
        self.cart_ids += 1
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        # exista product cu qty != 0 ?
        # daca da, adauga l si scade qty
        for products in self.queue.values():  # { "product_id" : qty }
            if product in products:
                if products[product] > 0:  # avem qty pt el
                    shopping_list = self.carts[cart_id]
                    shopping_list.append(product)
                    self.carts[cart_id] = shopping_list
                    products[product] -= 1  # l am facut indisponibil
                    return True
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        shopping_list = self.carts[cart_id]
        shopping_list.remove(product)
        self.carts[cart_id] = shopping_list
        # product acum trebuie trecut disponibil pt ceilalti adica de crescut qty din queue
        for products in self.queue.values():
            if product in products:
                products[product] += 1  # l am facut disponibil


    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        return self.carts[cart_id]
