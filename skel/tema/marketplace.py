"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2022
"""
import threading
import logging
import time
import unittest
from logging.handlers import RotatingFileHandler


class TestMarketplaceMethods(unittest.TestCase):
    """
    Class that represents the unit testing for the Marketplace methods.
    """

    def setUp(self):
        """
        Constructor for setting up the tests
        Initialize the marketplace with queue_limit = 8
        """
        self.marketplace = Marketplace(8)

    def test_register_producer(self):
        """
        Test the register_producer func
        """
        # first register should always be 0
        self.assertEqual(self.marketplace.register_producer(), 0)
        # increment
        self.assertEqual(self.marketplace.register_producer(), 1)
        # next one should be 2 not 3
        self.assertNotEqual(self.marketplace.register_producer(), 3)

    def test_publish(self):
        """
        Test the publish func
        """
        # publish 8 times so we can test queue_limit
        for _ in range(8):
            self.assertEqual(self.marketplace.publish("0", "id1"), True)
        # should be False because queue is full
        self.assertEqual(self.marketplace.publish("0", "id1"), False)

    def test_new_cart(self):
        """
        Test the new_cart func
        """
        # first cart should always be 0
        self.assertEqual(self.marketplace.new_cart(), 0)
        # increment
        self.assertEqual(self.marketplace.new_cart(), 1)
        # next one should be 2 not 3
        self.assertNotEqual(self.marketplace.new_cart(), 3)

    def test_add_to_cart(self):
        """
        Test the add_to_cart func
        """
        # add to cart without a cart should be False
        self.assertEqual(self.marketplace.add_to_cart(0, "id1"), False)
        self.marketplace.new_cart()
        # add to cart a product which doesn't exist
        self.assertEqual(self.marketplace.add_to_cart(0, "id1"), False)
        self.marketplace.publish("0", "id1")
        # now should work with product published above
        self.assertEqual(self.marketplace.add_to_cart(0, "id1"), True)

    def test_remove_from_cart(self):
        """
        Test the remove_from_cart func
        """
        # publish 3 products
        self.marketplace.publish("0", "id1")
        self.marketplace.publish("0", "id2")
        self.marketplace.publish("0", "id1")
        # make a new cart
        self.marketplace.new_cart()
        # add all products
        self.marketplace.add_to_cart(0, "id1")
        self.marketplace.add_to_cart(0, "id2")
        self.marketplace.add_to_cart(0, "id1")
        # remove one
        self.marketplace.remove_from_cart(0, "id2")
        # len of cart should be 2
        self.assertEqual(len(self.marketplace.carts[0]) == 2, True)

    def test_place_order(self):
        """
        Test the place_order func
        """
        # publish 3 products
        self.marketplace.publish("0", "id1")
        self.marketplace.publish("0", "id2")
        self.marketplace.publish("0", "id3")
        # make a new cart
        self.marketplace.new_cart()
        # add all products
        self.marketplace.add_to_cart(0, "id1")
        self.marketplace.add_to_cart(0, "id2")
        self.marketplace.add_to_cart(0, "id3")
        # place order
        self.assertEqual(self.marketplace.place_order(0), ['id1', 'id2', 'id3'])


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

    # dictionary of type:
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
        self.handler = RotatingFileHandler('marketplace.log', maxBytes=100000, backupCount=30)
        logging.basicConfig(handlers=[self.handler], level=logging.INFO,
                            format='%(asctime)s %(levelname)s '
                                   ' - %(funcName)s: %(message)s')
        logging.Formatter.converter = time.gmtime

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        producer_id = self.producer_ids
        self.producer_ids += 1
        logging.info("registered producer")
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
        logging.info("start func with producer_id=%s, product=%s", producer_id, product)
        # if producer_id is the first time in the marketplace, it needs a new entry
        if producer_id not in self.queue:
            self.queue[producer_id] = {}
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
            logging.info("exit func ret=True")
            return True
        logging.info("exit func ret=False")
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        cart_id = self.cart_ids
        self.carts[cart_id] = []
        self.cart_ids += 1
        logging.info("created new cart")
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
        logging.info("start func with cart_id=%s, product=%s", cart_id, product)
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
                    logging.info("exit func with ret=True")
                    return True
        logging.info("exit func with ret=False")
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        logging.info("start func with cart_id=%s, product=%s")
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
        logging.info("start func with cart_id=%s and returned", cart_id)
        return self.carts[cart_id]
