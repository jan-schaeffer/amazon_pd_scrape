import random

random.seed(10101010)
alphabet = "ABCDEFGHHIJKLMNOPQRSTUVWXYZ"


def gen_password():
    password = ""
    i = 0
    while i <= 12:
        element = random.randrange(0, 9)
        element = str(element)
        letter_or_number = random.randrange(0, 2)
        if letter_or_number == 1:
            index = random.randrange(0, len(alphabet))
            element = alphabet[index]
            lower_or_upper = random.randrange(0, 2)
            if lower_or_upper == 1:
                element = element.lower()
        password = password + element
        i = i + 1
    return password


