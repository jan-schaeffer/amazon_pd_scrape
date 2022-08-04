# importing modules
import os
import time
import imaplib
import email
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WDV
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# setting up vars
path = os.getcwd()
imap_host = ""
imap_port = ""
url = "https://www.amazon.de/eltern"


def get_otp(login_data):
    imap_user = login_data["imap_user"]
    imap_pass = login_data["imap_pass"]

    # connect to host using SSL
    imap = imaplib.IMAP4_SSL(imap_host, imap_port, timeout=20)
    time.sleep(5)
    # login to server
    resp_code, response = imap.login(imap_user, imap_pass)
    # print("Response Code : {}".format(resp_code))
    # print("Response      : {}\n".format(response[0].decode()))
    imap.select("Inbox")  # imap.list() shows available folders
    tmp, data = imap.search(None, "ALL")  # '(FROM "konto-aktualisierung@amazon.de")')
    mail_list = data[0].split()  # data has numbers for all received mails
    num = mail_list[-1]  # gets number of latest mail
    tmp, data = imap.fetch(num, '(RFC822)')  # retrieve latest email
    data = data[0]  # the following narrows down data to only the html code
    data = data[1]
    msg = email.message_from_bytes(data)  # convert bytes object to message object
    # print(msg.is_multipart()) = TRUE
    msg = msg.get_payload(i=0, decode=False)  # msg is multipart, command returns 0th item of payload
    msg = msg.get_payload(i=None, decode=True)  # msg is not multipart anymore, i must be NONE, decodes to html
    mail_soup = BeautifulSoup(msg, "lxml")  # convert to soup
    otp = mail_soup.find("p", class_="otp").text  # find OTP

    return otp


def enter_otp(login_data, driver):
    print('getting otp')
    otp = get_otp(login_data)
    driver.find_element(By.ID, "cvf-input-code").send_keys(otp)
    WDV(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#cvf-submit-otp-button .a-button-input"))).click()
    return driver


def enter_new_pw(login_data, driver, new_pw_try, log):
    new_pass = login_data['new_pass']
    driver.find_element(By.ID, "ap_fpp_password").send_keys(new_pass)
    driver.find_element(By.ID, "ap_fpp_password_check").send_keys(new_pass)
    WDV(driver, 20).until(EC.element_to_be_clickable((By.ID, "continue"))).click()

    # check success
    page_soup = BeautifulSoup(driver.page_source, "lxml").text
    if 'Die Passwörter stimmen nicht überein' in page_soup:
        if new_pw_try == 1:
            log.append('not same pw')
            new_pw_try = new_pw_try + 1
            enter_new_pw(login_data, driver, new_pw_try, log)
        else:
            log.append('password could not be changed')
    elif 'Verwenden Sie ein anderes Passwort.' in page_soup:
        log.append('not same pw')
    elif 'Leider ist bei Ihrer Eingabe ein Problem bei uns aufgetreten.' in page_soup:
        log.append('problem pw')
        if new_pw_try == 1:
            print('not same')
            reset_pw(login_data, driver, log)
            new_pw_try = new_pw_try + 1
        else:
            log.append('password could not be changed')

    return login_data, driver, log


def password_changer(login_data, driver, log):
    name = login_data['imap_user']

    page_soup = BeautifulSoup(driver.page_source, "lxml").text
    if 'Ihr Passwort wurde geändert.' in page_soup:
        print('password changed')
        login_data['amz_pass'] = login_data['amz_pass_old']
        login_data['amz_pass'] = login_data['new_pass']
        del login_data['new_pass']
        log.append('password changed')

    elif "Ungültiger Code. Überprüfen Sie den Code, und versuchen Sie es dann erneut." in page_soup:
        print('code invalid')
        driver = enter_otp(login_data, driver)
        password_changer(login_data, driver, log)

    elif "Wie lautet der vollständige Name, der mit Ihrem Konto verknüpft ist?" in page_soup:
        print('security question')
        # answer security question
        WDV(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-button-input")))
        driver.find_element(By.CSS_SELECTOR, ".a-input-text").send_keys(name)
        WDV(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-button-input"))).click()
        password_changer(login_data, driver, log)

    elif 'ungewöhnliche Bewegungen' in page_soup:
        print('Suspicious')
        log.append('Suspicious')

    elif 'Neues Passwort erstellen' in page_soup and \
         'Wir fragen nach diesem Passwort, wenn Sie sich anmelden.' in page_soup:
        # enter password
        WDV(driver, 20).until(EC.element_to_be_clickable((By.ID, "continue")))
        new_pw_try = 1
        login_data, driver, log = enter_new_pw(login_data, driver, new_pw_try, log)

    else:
        log.append('some other error occurred trying to change pw.')

    return login_data, driver, log


def reset_pw(login_data, driver, log):
    # send otp
    WDV(driver, 20).until(EC.element_to_be_clickable((By.ID, "continue"))).click()
    # enter otp
    driver = enter_otp(login_data, driver)
    # check success
    login_data, driver, log = password_changer(login_data, driver, log)#
    driver.get(url)

    return login_data, driver, log
