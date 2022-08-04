# importing modules
import os
import time
import password_resetter
import mail_verifier
import captcha_solver
import kid_finder
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait as WDV
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import simpleaudio as sa

# setting up vars
path = os.getcwd()
imap_host = ""
imap_port = ""
url = "https://www.amazon.de/eltern"
logout = "https://www.amazon.de/gp/flex/sign-out.html?path=%2Fgp%2Fyourstore%2Fhome&signIn=1&useRedirectOnSuccess=1&action=sign-out&ref_=nav_AccountFlyout_signout"


def login_controller(login_data, driver, log, pw_try):
    if pw_try > 1:
        print(f'password try: {pw_try}')
    page_soup = BeautifulSoup(driver.page_source, "lxml").text

    if "Konto wurde wegen Missbrauchs" in page_soup:
        log.append("Missbrauch")

    elif 'Konto gesperrt' in page_soup:
        log.append("Missbrauch")

    elif "Zurücksetzen des Passworts erforderlich" in page_soup:
        log.append("Password must be reset")
        login_data, driver, log = password_resetter.reset_pw(login_data, driver, log)
        login_controller(login_data, driver, log, pw_try)

    elif 'Geben Sie eine gültige E-Mail-Adresse oder Mobiltelefonnummer ein.' in page_soup:
        log.append('email invalid')

    # deal with cookie popup if necessary
    elif "Cookie-Einstellungen" in page_soup:
        WDV(driver, 20).until(EC.element_to_be_clickable((By.ID, "sp-cc-accept"))).click()
        login_controller(login_data, driver, log, pw_try)

    # deal with any other issue if not diretly on overview page
    elif "Aktivität Ihres Kindes" not in page_soup:

        if "Loslegen" in page_soup:
            WDV(driver, 20).until(EC.element_to_be_clickable((By.TAG_NAME, "button"))).click()
            time.sleep(2)
            login_controller(login_data, driver, log, pw_try)

        elif "kein Konto mit dieser E-Mail-Adresse" in page_soup:
            log.append("No account")

        elif "Falsches Passwort" in page_soup:
            amz_pass = login_data['amz_pass']
            print("Wrong password")
            if pw_try == 1:
                driver.find_element(By.ID, "ap_password").send_keys(amz_pass)
                WDV(driver, 20).until(EC.element_to_be_clickable((By.ID, "signInSubmit"))).click()
                pw_try = pw_try + 1
                login_controller(login_data, driver, log, pw_try)
            else:
                log.append("wrong pw. 2 retries")

        # Mobilnummer hinzufügen
        elif "Mobiltelefonnummer hinzufügen" in page_soup:
            WDV(driver, 20).until(EC.element_to_be_clickable((By.ID, "ap-account-fixup-phone-skip-link"))).click()
            login_controller(login_data, driver, log, pw_try)

        # Verify Mail
        elif "Genehmigen Sie zu Ihrer Sicherheit die Benachrichtigung, die gesendet wurde an:" in page_soup:
            print("Verifying mail")
            log.append("Verifying mail")
            mail_try = 1
            try:
                driver = mail_verifier.verify_mail(login_data, driver, mail_try)
                login_controller(login_data, driver, log, pw_try)
            except Exception:
                log.append("Mail could not be verified")

        # CAPTCHA
        elif "die Zeichen ein, die in der Abbildung unten gezeigt werden" in page_soup:
            print('Captcha')
            # c_try = captcha try number, c_pw_try = captcha password try number
            c_try = c_pw_try = 1
            driver, log = captcha_solver.solve_captcha(login_data, driver, c_try, c_pw_try, log)
            login_controller(login_data, driver, log, pw_try)

    # if we are on overview page
    elif "Aktivität Ihres Kindes" in page_soup:
        print("we are on overview")
        log = kid_finder.find_kids(driver, log, login_data)

    return login_data, log


def login(login_data, log):
    amz_user = login_data["amz_user"]
    amz_pass = login_data["amz_pass"]
    # open chrome
    service = Service(f"{path}/chromedriver")
    options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'})
    driver.get(url)

    try:
        # go to login page
        WDV(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-button-input"))).click()
        # enter credentials
        WDV(driver, 20).until(EC.element_to_be_clickable((By.ID, "signInSubmit")))
        driver.find_element(By.ID, "ap_email").send_keys(amz_user)
        driver.find_element(By.ID, "ap_password").send_keys(amz_pass)
        WDV(driver, 20).until(EC.element_to_be_clickable((By.ID, "signInSubmit"))).click()
        time.sleep(2)
        # check success
        pw_try = 1
        login_data, log = login_controller(login_data, driver, log, pw_try)
        driver.get(logout)

    except Exception:
        log.append('unspecified error')
        wave_obj = sa.WaveObject.from_wave_file(f'{path}/pluck.wav')
        play_obj = wave_obj.play()
        play_obj.wait_done()
        driver.quit()

    return login_data, log
