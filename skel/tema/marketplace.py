"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2022
"""
import threading


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    # generate an id for every producer that calls register_producer()
    producer_ids: int
    # nested dictionary of type:
    # { "producer_id" : { "product_id" : qty } }
    queue: dict

    # nested dictionary of type:
    # { "cart_id" : [] }, where [] = list of products from the cart
    carts: dict
    cart_ids: int

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
        # if producer_id is the first time in the marketplace, it needs a new entry
        if producer_id not in self.queue:
            self.queue[producer_id] = {}
        else:
            # products is a dictionary of type { "product_id" : qty}
            products = self.queue[producer_id]
            # check if it didn't cross the limit by summing up the qtys
            current_size = sum(products.values())
            if current_size < self.queue_size_per_producer:
                # check if the current product doesn't exist and add it with qty = 1
                if product not in products:
                    products[product] = 1  # product is product_id and 1 represents the qty
                # if it already exists just increment the qty
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
        self.carts[cart_id] = []
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
        # is there this product with qty != 0?
        # if yes, add it then decrement the qty
        # in this way, the product will be unavailable to other consumers
        for products in self.queue.values():
            if product in products:
                if products[product] > 0:
                    shopping_list = self.carts[cart_id]
                    shopping_list.append(product)
                    self.carts[cart_id] = shopping_list
                    products[product] -= 1  # make it unavailable
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
        for products in self.queue.values():
            if product in products:
                products[product] += 1  # make it available

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        return self.carts[cart_id]
