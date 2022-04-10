"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Thread
from time import sleep


class Producer(Thread):
    """
    Class that represents a producer.
    """
    # preluat din marketplace din register_producer() si folosit la publish() ulterior
    id_producer: int

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        # lista de tipul: ["id", cantitate, publish_cooldown]
        self.products = products
        # referinta la marketplace
        self.marketplace = marketplace
        # cand limit e la maxim, asteapta acest timp
        self.republish_wait_time = republish_wait_time


    def run(self):
        with self.marketplace.lock:
            self.id_producer = self.marketplace.register_producer()
        while True:
            for item in self.products:
                (product_id, qty, publish_cooldown) = item
                for _ in range(qty):
                    while True:
                        is_ok = self.marketplace.publish(self.id_producer, product_id)
                        sleep(publish_cooldown)
                        if is_ok is False:
                            sleep(self.republish_wait_time)
                        else:
                            break
