# importing modules
import os
import time
import wget
import password_resetter
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WDV
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from twocaptcha import TwoCaptcha

# setting up vars
path = os.getcwd()
solver = TwoCaptcha("")


def solve_captcha(login_data, driver, c_try, c_pw_try, log):
    amz_pass = login_data["amz_pass"]

    if c_try < 5 and c_pw_try < 2:
        # enter password again
        # WDV(driver, 20).until(EC.element_to_be_clickable((By.NAME, "signInSubmit")))
        driver.find_element(By.ID, "ap_password").send_keys(amz_pass)

        # find captcha link
        captcha_soup = BeautifulSoup(driver.page_source, "lxml")
        captcha_soup = captcha_soup.find("div", id="auth-captcha-image-container")
        captcha_soup = captcha_soup.contents[1]
        captcha_url = captcha_soup.get("src")
        # print(captcha_url)

        # download captcha to disk
        time_now = datetime.now().time()
        wget.download(captcha_url, f"{path}/captcha_imgs/{time_now}.jpg")

        # send image to 2captcha
        captcha_key = solver.normal(f"{path}/captcha_imgs/{time_now}.jpg")
        captcha_key = captcha_key["code"]

        # delete file
        os.remove(f"{path}/captcha_imgs/{time_now}.jpg")

        # enter key
        driver.find_element(By.ID, "auth-captcha-guess").send_keys(captcha_key)
        WDV(driver, 20).until(EC.element_to_be_clickable((By.ID, "signInSubmit"))).click()

        time.sleep(2)
        page_soup = BeautifulSoup(driver.page_source, "lxml").text
        if "Falsches Passwort" in page_soup:
            print('wrong password')
            c_pw_try = c_pw_try+1
            solve_captcha(login_data, driver, c_try, c_pw_try, log)

        elif "Zurücksetzen des Passworts erforderlich" in page_soup:
            print('password must be reset')
            log.append("Password must be reset")
            login_data, driver, log = password_resetter.reset_pw(login_data, driver, log)

        elif "Ein Problem ist aufgetreten:" in page_soup and \
             'Es konnte kein Konto mit dieser E-Mail-Adresse gefunden werden.' in page_soup and \
             'Geben Sie die Zeichen so ein, wie sie auf dem Bild erscheinen.' in page_soup:
            print('no account found')
            log.append('No account found')

        elif "Konto gesperrt" in page_soup:
            print('Missbrauch')
            log.append("Missbrauch")

        elif "gültige E-Mail" in page_soup:
            print('invalid mail')
            log.append("invalid email")

        elif 'ungewöhnliche Bewegungen' in page_soup:
            print('Suspicious')
            log.append('Suspicious')

        elif "Passworthilfe" in page_soup:
            print('pw help')
            log.append('password help')

        elif "Ein Problem ist aufgetreten:" in page_soup and \
             "Zeichen so ein, wie sie auf dem Bild erscheinen." in page_soup:
            print('wrong captcha')
            c_try = c_try+1
            solve_captcha(login_data, driver, c_try, c_pw_try, log)

    else:
        log.append('Captcha could not be solved')

    return driver, log
