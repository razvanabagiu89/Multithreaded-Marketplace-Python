# Marketplace with Multiple Producers Multiple Consumers with Python   

## About

https://ocw.cs.pub.ro/courses/asc/teme/tema1

By using the MPMC model, implement using multi-threading, logging and unit testing
a marketplace in which producers put products in their own queues, and consumers
take them out independently of the others without generating deadlocks or
inefficient delays.

## How to run the tests

- run local bash script in skel folder provided by ASC team.

## Structure & Flow

### For solving the tasks I used the following modules:

- marketplace.py
  - the marketplace contains two dictionaries:
    - queue is a nested dictionary containing the primary key the producer_id and then the interior
  dictionary is made up of products and their quantity.
    - the cart is a dictionary containing the key of the cart id and a list associated with it that
  will contain all the products added to the cart by the consumers.
  
  - register_producer()
    - will assign a unique id to the producer calling it.
  - publish(producer_id, product)
    - will publish the product from the parameters by first checking
  if the producer_id has any other products in the marketplace and if so,
  it will go to its own dictionary and publish the product there by checking
  if the product is already there, otherwise creating the entry.
  If it is, it will first check if the queue limit is not reached, then
  it'll increment its quantity or if it's not, it'll create the entry
  with quantity as one.
  - new_cart()
    - will assign a unique id of a cart to the consumer calling it.
  - add_to_cart(cart_id, product)
    - checks if the product exists in the marketplace and if the
  marketplace has any quantity for it. If so it will add it to the
  consumer's cart and make it unavailable to the other consumers
  by decrementing its quantity in the marketplace.
  - remove_from_cart(cart_id, product)
    - self explanatory, will remove the product then increment
  back the quantity, so it will be available to the other consumers.
  - place_order
    - will return a full list of all objects added to the cart
  by the consumer.

- producer.py
  - the producer has a 'while True' because he needs to keep on
creating sequentially its product and wait a publish_time,
then add them to their queue. If the queue is full, the producer will 
sleep for a republish_wait_time and try again.

- consumer.py
  - the consumer will create multiple shopping carts, and use
operations like adding or removing from the carts different 
products. After all these operations are done, it will place the
order and print everything the consumer bought.

## Synchronization

All the synchronization was done using locks. The sleep was used
as it was required to sleep the cooldowns each entity has.

## Unit testing

TestMarketplaceMethods is the class used for unit testing located
in marketplace.py. It tests all the methods from this module in
different scenarios and has a 100% success rate.

## Logging

Logging is done using the logging module and a Rotating File Handler.
When the content is written to marketplace.log and reaches the max limit
of bytes, it will write to 30 more files and continue the logging.
All loggings are done using the INFO level as required to.
Also, the logging is done using GMT time to avoid time inconsistencies
on the local machine.

## Observations

By running the unit tests we notice this warning:
"ResourceWarning: unclosed file" and that is because of the
RotatingFileHandler not being used by the unit tests (not required to).
