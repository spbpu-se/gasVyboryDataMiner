import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from time import sleep
import pytesseract
import sys
import argparse
from PIL import Image
from subprocess import check_output
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

pytesseract.pytesseract.tesseract_cmd = "D:\\Tesseract\\tesseract.exe"


def solveCaptcha(browser):
    try:
        while True:
            check = browser.find_elements(by=By.ID, value="captchaImg")
            if len(check) == 0:
                break
            print("captcha is found!")
            sleep(1)
            for _ in check:
                _.screenshot('captcha.png')
            captch = str(pytesseract.image_to_string(Image.open('captcha.png'), config="outputbase digits"))
            if len(captch) < 5:
                browser.refresh()
                continue
            captch.rstrip()
            print(captch)
            browser.find_element(by=By.ID, value="captcha").send_keys(captch)
            browser.find_element(by=By.CLASS_NAME, value="button-send").click()
            print("captcha is solved!")
            browser.implicitly_wait(5)
    except (StaleElementReferenceException, NoSuchElementException):
        pass


def captcha(func):
    def wrapper(*arg, **kwarg):
        solveCaptcha(browser)
        func(*arg, **kwarg)

    return wrapper


def observeData(browser):
    data_filter = browser.find_element(by=By.CSS_SELECTOR, value="span.filter")
    data_filter.click()
    WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.ID, "start_date")))
    start_date = browser.find_element(by=By.ID, value="start_date")
    browser.implicitly_wait(1)
    start_date.clear()
    start_date.send_keys("01.01.2022")
    end_date = browser.find_element(by=By.ID, value="end_date")
    end_date.clear()
    end_date.send_keys("01.01.2023")
    browser.find_element(by=By.ID, value="calendar-btn-search").click()
    solveCaptcha(browser)
    links = browser.find_elements(by=By.XPATH, value="//a[@href]")
    links = links[26:]
    linkArr = []
    for link in links:
        linkArr.append(link.get_attribute('href'))
    for link in linkArr:
        browser.get(link)
        solveCaptcha(browser)
        browser.find_element(by=By.ID, value="standard-reports-name").click()
        solveCaptcha(browser)
        browser.find_element(by=By.LINK_TEXT, value="Сведения о кандидатах").click()
        solveCaptcha(browser)
        browser.find_element(by=By.LINK_TEXT, value="Результаты выборов").click()


if __name__ == '__main__':
    option = Options()
    option.add_argument("--disable-infobars")
    option.headless = True
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
    browser.get('http://www.vybory.izbirkom.ru/region/izbirkom')
    observeData(browser)
    browser.close()