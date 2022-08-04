import amz_scrape
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WDV
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


def find_kids(driver, log, login_data):
    # check if there are multiple kids
    page_soup = BeautifulSoup(driver.page_source, "lxml")
    kids = page_soup.find_all("p", class_="css-17945oj")
    if len(kids) == 1:
        WDV(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".BOOK > span"))).click()
        # wait for page to load
        time.sleep(2)
        page_soup = BeautifulSoup(driver.page_source, "lxml")
        kid_name = page_soup.find("p", class_="css-17945oj").get_text()
        log.append(f"1 kid found. name: {kid_name}")

        page_soup = page_soup.text
        page_soup = BeautifulSoup(driver.page_source, "lxml")
        if "Keine Aktivitäten in den letzten 90 Tagen" in page_soup:
            log.append("no activity")
        amz_scrape.scrape(driver, login_data, kid_name)

    elif len(kids) == 2:
        WDV(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[2]/div/div/div[2]/div/p/span"))).click()
        # wait for page to load
        time.sleep(2)
        page_soup = BeautifulSoup(driver.page_source, "lxml")
        kid_name = page_soup.find("p", class_="css-17945oj").get_text()
        log.append(f"2 kids found. kid 1 name: {kid_name}")
        page_soup = page_soup.text
        if "Keine Aktivitäten in den letzten 90 Tagen" in page_soup:
            log.append("kid 1. no activity")
        amz_scrape.scrape(driver, login_data, kid_name)

        driver.back()
        WDV(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[2]/div[5]/div[2]/div[2]/div/div/div[2]/div/p/span"))).click()
        # wait for page to load
        time.sleep(2)
        page_soup = BeautifulSoup(driver.page_source, "lxml")
        kid_name = (page_soup.find("p", class_="css-17945oj").get_text())
        log.append(f"kid 2 name: {kid_name}")
        page_soup = page_soup.text
        if "Keine Aktivitäten in den letzten 90 Tagen in den letzten 90 Tagen" in page_soup:
            log.append("kid2. no activity")
        amz_scrape.scrape(driver, login_data, kid_name)

    elif len(kids) > 2:
        log.append("more than 2 kids")

    return log

