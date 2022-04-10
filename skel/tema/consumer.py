"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import threading
from threading import Thread
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """
    # preluat din new_cart() si folosit ulterior
    # la add_to_cart(), remove_from_cart() si place_order()
    cart_id: int

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        # lista de dictionare de tipul:
        # ["type": "add",
        # "product": "id2",
        # "quantity": 1]
        self.carts_ops = carts
        # referinta la marketplace
        self.marketplace = marketplace
        # daca nu gaseste produsul pe care il vrea in queue, va astepta acest timp
        self.retry_wait_time = retry_wait_time
        # propriul shopping cart ce va fi preluat din new_cart()
        # self.cart_id = self.marketplace.new_cart()

        self.lock = threading.Lock()

    def run(self):
        for ops in self.carts_ops:
            with self.marketplace.lock:
                self.cart_id = self.marketplace.new_cart()
            # op e dictionar de tipul ["type": "add", "product": "id2", "quantity": 1]
            for operation in ops:
                if operation["type"] == "add":
                    for _ in range(operation["quantity"]):
                        while True:
                            with self.marketplace.lock:
                                is_ok = self.marketplace.add_to_cart(
                                    self.cart_id, operation["product"])
                            if is_ok is False:
                                sleep(self.retry_wait_time)
                            else:
                                break
                elif operation["type"] == "remove":
                    for _ in range(operation["quantity"]):
                        with self.marketplace.lock:
                            self.marketplace.remove_from_cart(self.cart_id, operation["product"])

            with self.marketplace.lock:
                final_list = self.marketplace.place_order(self.cart_id)
                for item in final_list:
                    print(f"{self.name} bought {item}")
