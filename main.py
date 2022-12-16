import os.path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pytesseract
from PIL import Image
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import jsons
from urllib.parse import urlparse, parse_qs
import re
import logging
import sys
from sys import platform
from pymongo import MongoClient
from selenium.common.exceptions import TimeoutException
import time
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

envir = os.environ
DEBUG = False
if platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = "D:\\Tesseract\\tesseract.exe"

election_levels = {
    "federal": '//*[starts-with(@id, "select2-urovproved-result-") and "1" = substring(@id, string-length(@id))]',
    "regional": '//*[starts-with(@id, "select2-urovproved-result-") and "2" = substring(@id, string-length(@id))]',
    "regional_capital": '//*[starts-with(@id, "select2-urovproved-result-") and "3" = substring(@id, string-length(@id))]',
    "local": '//*[starts-with(@id, "select2-urovproved-result-") and "4" = substring(@id, string-length(@id))]'
}

client = MongoClient(envir["mongo_ip"], int(envir["mongo_port"]), username=envir["mongo_usr"],
                     password=envir["mongo_pwd"])
db = client.gas_vybory


def goThroughUiks(browser, uik, json_candidates):
    if len(browser.find_elements(by=By.XPATH, value=uik + '/ul/li/a')) == 0:
        recent_cands = []
        candidates = {_['candidate_id']: _['name'] for _ in json_candidates}
        table = browser.find_element(by=By.CLASS_NAME, value='table-bordered')
        if table:
            if table.text == "":
                return
            current_json_results = parseTable(browser, table, 'results')
            raw_candidates = current_json_results["candidates_results"][:]
            for i, cand in enumerate(raw_candidates):
                for p_id, p_name in candidates.items():
                    if cand[0] == p_name:
                        temp = next(item for item in json_candidates if item["name"] == p_name)
                        recent_cands.append(temp)
                        current_json_results["candidates_results"][i] = {'candidate_id': p_id, 'result': int(cand[1])}
                        break
            if db.results.find_one(current_json_results.copy()) is not None:
                return
            post_id = db.results.insert_one(current_json_results.copy())

            for candidate in recent_cands:
                candidate['oik_id'] = getOik(browser)
                if len(list(db.candidates.find({"candidate_id": candidate["candidate_id"]}))) > 0:
                     continue
                post_id = db.candidates.insert_one(candidate.copy())

    else:
        browser.find_elements(by=By.XPATH, value=uik)[0].click()
        solveCaptcha(browser)
        uik = uik + '/ul/li'
        links = browser.find_elements(by=By.XPATH, value=(uik + '/a'))
        linksArr = []
        for _ in links:
            if str(_.get_attribute('href')) not in "None":
                linksArr.append(str(_.get_attribute('href')))
        for _ in linksArr:
            browser.get(_)
            solveCaptcha(browser)
            goThroughUiks(browser, uik, json_candidates)


def getParameterFromQuery(browser, parameter):
    return int(parse_qs(urlparse(browser.current_url).query)[parameter][0])


def getOik(browser):
    res = re.findall(r'\d+', browser.find_element(by=By.CLASS_NAME, value='breadcrumb').text)
    if len(res) == 1:
        return 0
    return int(res[0]) if res else 0


def solveCaptcha(browser):
    try:
        while True:
            if 'DDoS' in browser.current_url:
                print("DDOS!")
                browser.back()
            check = browser.find_elements(by=By.ID, value="captchaImg")
            if len(check) == 0:
                break
            print("CAPTCHA!")
            try:
                WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, "captchaImg")))
            except TimeoutException:
                browser.refresh()
            time.sleep(1)
            for _ in check:
                _.screenshot('captcha.png')
            captch = str(pytesseract.image_to_string(Image.open('captcha.png'), config="outputbase digits"))
            if len(captch) < 5:
                browser.refresh()
                continue
            captch.rstrip()
            browser.find_element(by=By.ID, value="captcha").send_keys(captch)
            browser.find_element(by=By.CLASS_NAME, value="button-send").click()
    except (StaleElementReferenceException, NoSuchElementException):
        pass


def flatTo2DList(list, rowSize):
    return [[*list[rowSize * i: rowSize * i + rowSize]] for i in range(int(len(list) / rowSize))]


def parseTable(browser, table, type='results', table_format="221", jsn=None):
    raw_data = []
    rows_table = table.find_elements(by=By.TAG_NAME, value="tr")
    for row in rows_table:
        columns_table = row.find_elements(by=By.TAG_NAME, value="td")
        for column in columns_table:
            if not column.text:
                raw_data.append("null")
                continue
            if column.text == ' ':
                raw_data.append("null")
                raw_data.append("null")
                continue
            raw_data.append(column.text)
    if type == 'results':
        rows_data = {'cand': []}
        raw_rows_data = flatTo2DList(raw_data, 3)
        is_candidates = False
        for row_data in raw_rows_data:
            if row_data[0] == 'null':
                is_candidates = True
                continue
            if is_candidates:
                row_data[2] = row_data[2].split('\n')[0]
                rows_data['cand'].append(row_data[1:])
            else:
                rows_data[row_data[1]] = int(row_data[2])

        if "3" not in rows_data:
            rows_data["3"] = 0

        json_oik = jsons.JsonVrnOik
        json_oik['vrn'] = getParameterFromQuery(browser, "vrn")
        json_oik['oik_id'] = getOik(browser)

        json = jsons.JsonComission

        json["vrn"] = getParameterFromQuery(browser, "vrn")
        json["oik_id"] = getOik(browser)
        json["uik_id"] = int(str(re.findall(r'\d+', browser.find_element(by=By.XPATH,
                                                                         value='//*[@id="report-body col"]/div[10]/div/table[2]/tbody/tr/td[2]/b').text)[
                                     0]
                                 if browser.find_element(By.XPATH,
                                                         value='//*[@id="report-body col"]/div[10]/div/table[2]/tbody/tr/td[2]/b') else 0))
        json["total_voters"] = rows_data[[_ for _ in rows_data if "избирателей" in _][0]]
        json["recieved_ballots"] = rows_data[[_ for _ in rows_data if "полученных" in _ or "полученнных" in _][0]]
        before_counter = [rows_data[a] for a in [_ for _ in rows_data if "досрочно" in _]]
        json["issued_ballots_inside"] = rows_data[[_ for _ in rows_data if
                                                   "в помещении" in _ or "в УИК" in _ or "на избирательном участке" in _ or "на участке" in _ or "в помещениях" in _][
            0]] + sum(
            int(cnt) for cnt in before_counter)
        json["issued_ballots_outside"] = rows_data[[_ for _ in rows_data if
                                                    "вне помещения" in _ or "вне УИК" in _ or "вне участка" in _ or "вне помещений" in _][
            0]]
        json["not_used_ballots"] = rows_data[[_ for _ in rows_data if "погашенных" in _][0]]
        json["ballots_from_outside_boxes"] = rows_data[[_ for _ in rows_data if "в переносных ящиках" in _][0]]
        json["ballots_from_inside_boxes"] = rows_data[[_ for _ in rows_data if "в стационарных ящиках" in _][0]]
        json["invalid_ballots"] = rows_data[[_ for _ in rows_data if "недействительных" in _][0]]
        json["lost_ballots"] = rows_data[[_ for _ in rows_data if "утраченных" in _ or "утерянных" in _][0]]
        json["not_counted_recieved_ballots"] = rows_data[
            [_ for _ in rows_data if
             "не учтенных" in _ or "неучтенных" in _ or "не учтённых" in _ or "неучтённых" in _][0]]
        json["candidates_results"] = rows_data["cand"]
        if json["uik_id"] == json["oik_id"]:
            json["uik_id"] = 0
        json_oik["uik_id"] = json["uik_id"]
        if db.districts.find_one(json_oik.copy()) is not None:
            return json
        post_id = db.districts.insert_one(json_oik.copy())
        return json
    if type == 'candidates':
        raw_rows_data = flatTo2DList(raw_data, (8 if table_format == "220" else 7))
        candidates = []

        for rows_data in raw_rows_data:
            candidate = dict(jsons.JsonCandidate)
            candidate["vrn"] = getParameterFromQuery(browser, "vrn")
            candidate["name"] = rows_data[1]
            candidate["dob"] = rows_data[2]
            candidate["subject_of_nominmation"] = rows_data[3]
            candidate["nomination"] = rows_data[5] if table_format == "220" else rows_data[4]
            candidate["registration"] = rows_data[6] if table_format == "220" else rows_data[5]
            candidate["elected"] = rows_data[7] if table_format == "220" else rows_data[6]
            candidates.append(candidate)
        return candidates
    if type == 'candidate':
        raw_rows_data = flatTo2DList(raw_data, 3)
        jsn["candidate_id"] = getParameterFromQuery(browser, "vibid")
        jsn["place_of_birth"] = raw_rows_data[2][2]
        jsn["place_of_living"] = raw_rows_data[3][2]
        jsn["education"] = raw_rows_data[4][2]
        jsn["employer"] = raw_rows_data[5][2]
        jsn["position"] = raw_rows_data[6][2]
        jsn["deputy_info"] = raw_rows_data[7][2]
        jsn["criminal_record"] = raw_rows_data[8][2]
        jsn["inoagent"] = raw_rows_data[9][2]
        jsn["status"] = raw_rows_data[10][2]
        return jsn


def parseTableByXPATH(browser, xpath, type='results', table_format="221", jsn=None):
    table = browser.find_element(by=By.XPATH,
                                 value=xpath)
    return parseTable(browser, table, type, table_format, jsn)


def extendCandidates(browser, link=None):
    current_json_candidates = []
    tableArr = []
    if link is not None:
        browser.get(link)
    tables = ['//*[@id="candidates-221-2"]/tbody', '//*[@id="candidates-220-2"]/tbody']
    table = browser.find_elements(by=By.XPATH, value='//*[@id="candidates-221-2"]/tbody/tr/td/a')
    if len(table) <= 0:
        table = browser.find_elements(by=By.XPATH, value='//*[@id="candidates-221-2"]/tbody/tr/td/nobr/a')
    table2 = browser.find_elements(by=By.XPATH, value='//*[@id="candidates-220-2"]/tbody/tr/td/a')
    if len(table2) <= 0:
        table2 = browser.find_elements(by=By.XPATH, value='//*[@id="candidates-220-2"]/tbody/tr/td/nobr/a')
    bln = len(browser.find_elements(by=By.XPATH, value=tables[0])) > 0
    if len(table) <= 0 and len(table2) <= 0:
        return -1, -1
    temp = list(parseTableByXPATH(browser, tables[0] if bln else tables[1],
                                  type="candidates", table_format=("221" if bln else "220")))
    current_json_candidates.extend(temp)
    actual_table = table if len(table) > 0 else table2
    for _ in actual_table:
        tableArr.append(_.get_attribute('href'))
    return current_json_candidates, tableArr


def parseCandidates(browser):
    tableArr = []
    listsArr = []
    current_json_candidates = []
    browser.find_element(by=By.XPATH, value="/html/body/div[2]/main/div[2]/div[2]/div[1]/ul/li/a[2]").click()
    if len(browser.find_elements(by=By.XPATH, value='//*[@id="report-body col"]/div[10]/div/div[5]/ul[1]/li/a')) > 0:
        tempCandidates, tempTable = extendCandidates(browser)
        if tempCandidates == -1 and tempTable == -1:
            return "continue"
        tableArr.extend(tempTable)
        current_json_candidates.extend(tempCandidates)
        for _ in browser.find_elements(by=By.XPATH, value='//*[@id="report-body col"]/div[10]/div/div[5]/ul[1]/li/a'):
            listsArr.append(_.get_attribute('href'))
        for _ in listsArr:
            tempCandidates, tempTable = extendCandidates(browser, _)
            if tempCandidates == -1 and tempTable == -1:
                return "continue"
            tableArr.extend(tempTable)
            current_json_candidates.extend(tempCandidates)
        for i in range(len(tableArr)):
            browser.get(tableArr[i])
            solveCaptcha(browser)
            parseTableByXPATH(browser, '//*[@id="report-body col"]/div[10]/div/div[2]/table', type="candidate",
                              jsn=current_json_candidates[i])
            solveCaptcha(browser)
        return current_json_candidates
    else:
        tables = ['//*[@id="candidates-221-2"]/tbody', '//*[@id="candidates-220-2"]/tbody']
        table = browser.find_elements(by=By.XPATH, value='//*[@id="candidates-221-2"]/tbody/tr/td/a')
        if len(table) <= 0:
            table = browser.find_elements(by=By.XPATH, value='//*[@id="candidates-221-2"]/tbody/tr/td/nobr/a')
        table2 = browser.find_elements(by=By.XPATH, value='//*[@id="candidates-220-2"]/tbody/tr/td/a')
        if len(table2) <= 0:
            table2 = browser.find_elements(by=By.XPATH, value='//*[@id="candidates-220-2"]/tbody/tr/td/nobr/a')
        bln = len(browser.find_elements(by=By.XPATH, value=tables[0])) > 0
        if len(table) <= 0 and len(table2) <= 0:
            return "continue"
        current_json_candidates = parseTableByXPATH(browser, tables[0] if bln else tables[1],
                                                    type="candidates", table_format=("221" if bln else "220"))
        actual_table = table if len(table) > 0 else table2
        actual_table = actual_table
        tableArr = []
        for _ in actual_table:
            tableArr.append(_.get_attribute('href'))
        for i in range(len(tableArr)):
            browser.get(tableArr[i])
            solveCaptcha(browser)
            parseTableByXPATH(browser, '//*[@id="report-body col"]/div[10]/div/div[2]/table', type="candidate",
                              jsn=current_json_candidates[i])
        solveCaptcha(browser)
        return current_json_candidates


def observeData(browser):
    solveCaptcha(browser)
    data_filter = browser.find_element(by=By.CSS_SELECTOR, value="span.filter")
    data_filter.click()
    WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.ID, "start_date")))
    start_date = browser.find_element(by=By.ID, value="start_date")
    browser.implicitly_wait(1)
    start_date.clear()
    start_date.send_keys(envir["start_date"])
    end_date = browser.find_element(by=By.ID, value="end_date")
    end_date.clear()
    end_date.send_keys(envir["end_date"])
    WebDriverWait(browser, 2).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="search_form"]/div/div[2]/div[1]/span/span[1]/span/span/textarea')))
    browser.find_element(by=By.XPATH,
                         value='//*[@id="search_form"]/div/div[2]/div[1]/span/span[1]/span/span/textarea').click()
    browser.find_element(by=By.XPATH, value=election_levels[envir["level"]]).click()
    browser.find_element(by=By.XPATH, value='//*[@id="urovproved-close-drpdown-btn"]').click()
    browser.find_element(by=By.XPATH, value='//*[@id="calendar-btn-search"]').click()
    solveCaptcha(browser)
    links = browser.find_elements(by=By.XPATH, value="//a[@href]")
    links = links[26:]
    linkArr = []
    for link in links:
        linkArr.append(link.get_attribute('href'))
    print("all %i links are stacked!" % (len(linkArr)))
    for link in linkArr:
        # Кандидаты
        if os.path.exists(str("output/") + str(link.split('vrn=')[1].split('&')[0]) + str(".json")):
            continue
        browser.get(link)
        solveCaptcha(browser)
        print(link)
        reports_name = browser.find_element(by=By.ID, value="standard-reports-name")
        if reports_name.is_displayed() is False:
            continue
        reports_name.click()
        solveCaptcha(browser)
        if len(browser.find_elements(by=By.LINK_TEXT, value="Сведения о кандидатах")) == 1:
            browser.find_element(by=By.LINK_TEXT, value="Сведения о кандидатах").click()
        else:
            if len(browser.find_elements(by=By.LINK_TEXT,
                                         value="Сведения о кандидатах, выдвинутых по одномандатным (многомандатным) избирательным округам")) == 1:
                browser.find_element(by=By.LINK_TEXT,
                                     value="Сведения о кандидатах, выдвинутых по одномандатным (многомандатным) избирательным округам").click()

        solveCaptcha(browser)
        raw_candidates = parseCandidates(browser)
        if raw_candidates == "continue":
            continue
        # УИКи
        browser.get(link)
        solveCaptcha(browser)
        date_of_vote = browser.find_element(by=By.XPATH, value='//*[@id="election-info"]/div/div[3]/div[2]/b').text
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Результаты выборов")))
        browser.find_element(by=By.LINK_TEXT, value="Результаты выборов").click()
        solveCaptcha(browser)
        resBtn = browser.find_element(by=By.XPATH, value='//*[@id="election-results"]/table/tbody/tr/td/a')
        if resBtn.text not in (
                "Результаты выборов", "Результаты выборов по одномандатному (многомандатному) округу",
                "Данные о предварительных итогах голосования по одномандатному (многомандатному) округу"):
            continue
        else:
            resBtn.click()
            solveCaptcha(browser)

        current_json_vrn = jsons.JsonVrn
        current_json_vrn["vrn"] = getParameterFromQuery(browser, "vrn")
        current_json_vrn["title"] = str(
            browser.find_element(by=By.XPATH, value='//*[@id="election-title"]').text.split('\n')[0])
        current_json_vrn["level"] = envir["level"]
        current_json_vrn["date"] = datetime.strptime(date_of_vote, '%d.%m.%Y').date()
        if db.elections.find_one(current_json_vrn.copy()) is not None:
            continue
        post_id = db.elections.insert_one(current_json_vrn.copy())
        goThroughUiks(browser, '/html/body/div[2]/main/div[2]/div[2]/div[1]/ul/li', raw_candidates)
    browser.get('http://www.vybory.izbirkom.ru/region/izbirkom')


if __name__ == '__main__':
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--no-sandbox")
    option.headless = not DEBUG
    browser = webdriver.Chrome(options=option)
    browser.get('http://www.vybory.izbirkom.ru/region/izbirkom')
    observeData(browser)
    browser.close()
