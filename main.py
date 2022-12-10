from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
import pytesseract
from PIL import Image
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import jsons
import jsonpickle
from urllib.parse import urlparse, parse_qs
import re

pytesseract.pytesseract.tesseract_cmd = "D:\\Tesseract\\tesseract.exe"

DEBUG = True
election_levels = {
    "federal": '//*[@id="select2-urovproved-result-gyua-1"]',
    "regional": '//*[@id="select2-urovproved-result-q3ub-2"]',
    "regional_capital": '//*[@id="select2-urovproved-result-aftx-3"]',
    "local": '//*[@id="select2-urovproved-result-5sgy-4"]'
}


def solveCaptcha(browser):
    try:
        while True:
            if 'DDoS' in browser.current_url():
                browser.back()
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
    except (StaleElementReferenceException, NoSuchElementException):
        pass


def parseTableByXPATH(browser, xpath, json, type='election-results'):
    table = browser.find_element(by=By.XPATH,
                                 value=xpath)
    raw_data = []
    rows_table = table.find_elements(by=By.TAG_NAME, value="tr")
    for row in rows_table:
        columns_table = row.find_elements(by=By.TAG_NAME, value="td")
        for column in columns_table:
            if column.text == '':
                raw_data.append("null")
            raw_data.append(column.text)
    if type == 'election-results':
        pass


def parseCandidates(browser, json):
    links = ['//*[@id="candidates-221-2"]/tbody/tr/td/nobr/a', '//*[@id="candidates-220-2"]/tbody/tr/td/nobr/a']
    tables = ['//*[@id="candidates-221-2"]/tbody', '//*[@id="candidates-220-2"]/tbody']
    table = browser.find_elements(by=By.XPATH, value=links[0])
    table2 = browser.find_elements(by=By.XPATH, value=links[1])
    actual_table = table if not None else table2
    parseTableByXPATH(browser, tables[0] if table is not None else tables[1], json)
    tableArr = []
    for _ in actual_table:
        tableArr.append(_.get_attribute('href'))
    for _ in tableArr:
        browser.get(_)
        solveCaptcha(browser)
        parseTableByXPATH(browser, '//*[@id="report-body col"]/div[10]/div/div[2]/table', json)


def observeData(browser):
    for level in election_levels:
        data_filter = browser.find_element(by=By.CSS_SELECTOR, value="span.filter")
        data_filter.click()
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.ID, "start_date")))
        start_date = browser.find_element(by=By.ID, value="start_date")
        browser.implicitly_wait(1)
        start_date.clear()
        start_date.send_keys("01.01.2022")
        end_date = browser.find_element(by=By.ID, value="end_date")
        end_date.clear()
        end_date.send_keys("01.03.2022")
        browser.find_element(by=By.XPATH,
                             value='//*[@id="search_form"]/div/div[2]/div[1]/span/span[1]/span/span/textarea').click()
        browser.find_element(by=By.XPATH, value=election_levels[level]).click()
        browser.find_element(by=By.ID, value="calendar-btn-search").click()
        solveCaptcha(browser)
        links = browser.find_elements(by=By.XPATH, value="//a[@href]")
        links = links[26:]
        linkArr = []
        for link in links:
            linkArr.append(link.get_attribute('href'))
        print("all %i links are stacked!" % (len(linkArr)))
        for link in linkArr:
            print(link)
            browser.get(link)
            solveCaptcha(browser)
            browser.find_element(by=By.LINK_TEXT, value="Результаты выборов").click()
            solveCaptcha(browser)
            if browser.find_element(by=By.XPATH,
                                    value='//*[@id="election-results"]/table/tbody/tr/td/a').text not in (
            "Результаты выборов"):
                continue

            current_json_vrn = jsons.JsonVrn()

            current_json_vrn.vrn = int(parse_qs(urlparse(browser.current_url).query)[bytes('vrn')][0])
            current_json_vrn.title = browser.find_element(by=By.XPATH, value='//*[@id="election-title"]').text.split('\n')[0]
            current_json_vrn.level = level
            current_json_vrn.date = browser.find_element(by=By.XPATH, value='//*[@id="report-body col"]/div[10]/div/table[1]/tbody/tr/td').text.split('&nbsp; ')[1]

            json_str = jsonpickle.encode(current_json_vrn)
            with open(str(current_json_vrn.vrn) + ".json", "w") as f:
                f.write(json_str)
                f.close()

            browser.find_element(by=By.XPATH, value='//*[@id="election-results"]/table/tbody/tr/td/a').click()
            solveCaptcha(browser)
            parseTableByXPATH(browser, '//*[@id="report-body col"]/div[10]/div/div[2]/table')

            browser.find_element(by=By.ID, value="standard-reports-name").click()
            solveCaptcha(browser)
            browser.find_element(by=By.LINK_TEXT, value="Сведения о кандидатах").click()
            solveCaptcha(browser)
            parseCandidates(browser)
            solveCaptcha(browser)
        browser.get('http://www.vybory.izbirkom.ru/region/izbirkom')


if __name__ == '__main__':
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.headless = not DEBUG
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
    browser.get('http://www.vybory.izbirkom.ru/region/izbirkom')
    observeData(browser)
    browser.close()
