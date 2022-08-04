import random


def random_order():
    order_list = []
    while True:
        x = random.randrange(1, 501, 1)
        if x not in order_list:
            order_list.append(x)
        if len(order_list) == 500:
            break

    return order_list


def sorted_order():
    order_list = []
    for i in range(1, 541):
        order_list.append(i)

    return order_list
