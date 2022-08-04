import os

path = os.getcwd()


def setup():
    try:
        os.mkdir(f"{path}/captcha_imgs")
        os.mkdir(f"{path}/csv_out")
    except Exception as e:
        print(e)
