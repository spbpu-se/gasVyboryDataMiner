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

pytesseract.pytesseract.tesseract_cmd = "D:\\Tesseract\\tesseract.exe"

DEBUG = True


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
    except (StaleElementReferenceException, NoSuchElementException):
        pass


def parseTableByXPATH(browser, xpath):
    table = browser.find_element(by=By.XPATH,
                                 value=xpath)
    rows_table = table.find_elements(by=By.TAG_NAME, value="tr")
    for row in rows_table:
        columns_table = row.find_elements(by=By.TAG_NAME, value="td")
        for column in columns_table:
            if column.text == '':
                print("null")
            print(column.text)
    print('-----------------------------------------------------')


def parseCandidates(browser):
    links = ['//*[@id="candidates-221-2"]/tbody/tr/td/nobr/a', '//*[@id="candidates-220-2"]/tbody/tr/td/nobr/a']
    tables = ['//*[@id="candidates-221-2"]/tbody', '//*[@id="candidates-220-2"]/tbody']
    table = browser.find_elements(by=By.XPATH, value=links[0])
    table2 = browser.find_elements(by=By.XPATH, value=links[1])
    actual_table = table if not None else table2
    parseTableByXPATH(browser, tables[0] if table is not None else tables[1])
    tableArr = []
    for _ in actual_table:
        tableArr.append(_.get_attribute('href'))
    for _ in tableArr:
        browser.get(_)
        solveCaptcha(browser)
        parseTableByXPATH(browser, '//*[@id="report-body col"]/div[10]/div/div[2]/table')


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
    end_date.send_keys("01.03.2022")
    browser.find_element(by=By.ID, value="calendar-btn-search").click()
    solveCaptcha(browser)
    links = browser.find_elements(by=By.XPATH, value="//a[@href]")
    links = links[26:]
    linkArr = []
    for link in links:
        linkArr.append(link.get_attribute('href'))
    print("links are stacked!")
    for link in linkArr:
        browser.get(link)
        solveCaptcha(browser)
        browser.find_element(by=By.LINK_TEXT, value="Результаты выборов").click()
        solveCaptcha(browser)
        if browser.find_element(by=By.XPATH,
                                value='//*[@id="election-results"]/table/tbody/tr/td/a').text != "Результаты выборов":
            continue
        browser.find_element(by=By.XPATH, value='//*[@id="election-results"]/table/tbody/tr/td/a').click()
        solveCaptcha(browser)
        parseTableByXPATH(browser, '//*[@id="report-body col"]/div[10]/div/div[2]/table')
        browser.find_element(by=By.ID, value="standard-reports-name").click()
        solveCaptcha(browser)
        browser.find_element(by=By.LINK_TEXT, value="Сведения о кандидатах").click()
        solveCaptcha(browser)
        parseCandidates(browser)
        solveCaptcha(browser)


if __name__ == '__main__':
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.headless = not DEBUG
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
    browser.get('http://www.vybory.izbirkom.ru/region/izbirkom')
    observeData(browser)
    browser.close()
