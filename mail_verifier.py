import time
import imaplib
import email
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WDV
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# setting up vars
imap_host = ""
imap_port = ""


def verify_mail(login_data, driver, mail_try):
    imap_user = login_data["imap_user"]
    imap_pass = login_data["imap_pass"]

    try:
        # login to mail server to retrieve url
        imap = imaplib.IMAP4_SSL(imap_host, imap_port, timeout=20)
        time.sleep(5)
        resp_code, response = imap.login(imap_user, imap_pass)
        # print("Response Code : {}".format(resp_code))
        # print("Response      : {}\n".format(response[0].decode()))
        imap.select("Inbox")  # imap.list() shows available folders
        url2 = ""
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
        links = mail_soup.find_all('a')
        url2 = links[0].get('href')

    except Exception:
        if mail_try < 3:
            mail_try = mail_try + 1
            verify_mail(login_data, driver, mail_try)
    finally:
        imap.close()

    # click verify
    driver.switch_to.new_window("tab")
    driver.get(url2)

    WDV(driver, 20).until(EC.element_to_be_clickable((By.NAME, "customerResponseApproveButton"))).click()
    time.sleep(5)

    return driver
