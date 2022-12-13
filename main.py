import os.path

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
import json
from urllib.parse import urlparse, parse_qs
import re
import sys
from sys import platform

DEBUG = True
if platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = "D:\\Tesseract\\tesseract.exe"

election_levels = {
    "federal": '//*[starts-with(@id, "select2-urovproved-result-") and "1" = substring(@id, string-length(@id))]',
    "regional": '//*[starts-with(@id, "select2-urovproved-result-") and "2" = substring(@id, string-length(@id))]',
    "regional_capital": '//*[starts-with(@id, "select2-urovproved-result-") and "3" = substring(@id, string-length(@id))]',
    "local": '//*[starts-with(@id, "select2-urovproved-result-") and "4" = substring(@id, string-length(@id))]'
}


def goThroughUiks(browser, uik, json_candidates):
    if len(browser.find_elements(by=By.XPATH, value=uik + '/ul/li')) == 0:
        candidates = {_['candidate_id']: _['name'] for _ in json_candidates}
        table = browser.find_element(by=By.CLASS_NAME, value='table-bordered')
        if table:
            if table.text == "":
                return
            current_json_results = parseTable(browser, table, 'results')
            if os.path.exists(str("output/") + str(current_json_results["vrn"]) + str("_") + str(
                    current_json_results["oik_id"]) + "_" + str(current_json_results["uik_id"]) + str(".json")):
                return
            raw_candidates = current_json_results["candidates_results"][:]
            for i, cand in enumerate(raw_candidates):
                for p_id, p_name in candidates.items():
                    if cand[0] == p_name:
                        current_json_results["candidates_results"][i] = {'candidate_id': p_id, 'result': int(cand[1])}
                        break
            json_name = str(current_json_results["vrn"]) + str("_") + str(current_json_results["oik_id"]) + "_" + str(
                current_json_results["uik_id"])
            saveJson(current_json_results, json_name)

            for candidate in json_candidates:
                candidate['oik_id'] = getOik(browser)
                saveJson(candidate, str(candidate["vrn"]) + str("_") + str(candidate["candidate_id"]))

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
            sleep(1)
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


def saveJson(jsn, fn):
    with open("output/" + fn + ".json", "w", encoding='utf8') as f:
        json.dump(jsn, f, ensure_ascii=False)


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

        # before_flag = False
        # if "досрочно" in raw_rows_data[2][1]:
        #     before_flag = True
        # inside_tik = False
        # if "досрочно " in raw_rows_data[3][1]:
        #     inside_tik = True
        tens = [key for key in rows_data.keys() if len(key) == 3]

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
        json["recieved_ballots"] = rows_data[[_ for _ in rows_data if "полученных" in _][0]]
        before_counter = [rows_data[a] for a in [_ for _ in rows_data if "досрочно" in _]]
        json["issued_ballots_inside"] = rows_data[[_ for _ in rows_data if "в помещении" in _ or "в УИК" in _ or "на избирательном участке" in _][0]] + sum(
            int(cnt) for cnt in before_counter)
        json["issued_ballots_outside"] = rows_data[[_ for _ in rows_data if "вне помещения" in _ or "вне УИК" in _][0]]
        json["not_used_ballots"] = rows_data[[_ for _ in rows_data if "погашенных" in _][0]]
        json["ballots_from_outside_boxes"] = rows_data[[_ for _ in rows_data if "в переносных ящиках" in _][0]]
        json["ballots_from_inside_boxes"] = rows_data[[_ for _ in rows_data if "в стационарных ящиках" in _][0]]
        json["invalid_ballots"] = rows_data[[_ for _ in rows_data if "недействительных" in _][0]]
        json["lost_ballots"] = rows_data[[_ for _ in rows_data if "утраченных" in _][0]]
        json["not_counted_recieved_ballots"] = rows_data[[_ for _ in rows_data if "не учтенных" in _ or "неучтенных" in _][0]]
        json["candidates_results"] = rows_data["cand"]
        if json["uik_id"] == json["oik_id"]:
            json["uik_id"] = 0
        json_oik["uik_id"] = json["uik_id"]
        saveJson(json_oik, '_'.join(map(str, (json_oik['vrn'], json_oik['oik_id']))))
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


def parseCandidates(browser):
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


def observeData(browser, dates):
    for level in election_levels:
        solveCaptcha(browser)
        data_filter = browser.find_element(by=By.CSS_SELECTOR, value="span.filter")
        data_filter.click()
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.ID, "start_date")))
        start_date = browser.find_element(by=By.ID, value="start_date")
        browser.implicitly_wait(1)
        start_date.clear()
        start_date.send_keys(dates[0])
        end_date = browser.find_element(by=By.ID, value="end_date")
        end_date.clear()
        end_date.send_keys(dates[1])
        WebDriverWait(browser, 2).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="search_form"]/div/div[2]/div[1]/span/span[1]/span/span/textarea')))
        browser.find_element(by=By.XPATH,
                             value='//*[@id="search_form"]/div/div[2]/div[1]/span/span[1]/span/span/textarea').click()
        browser.find_element(by=By.XPATH, value=election_levels[level]).click()
        browser.find_element(by=By.XPATH, value='//*[@id="urovproved-close-drpdown-btn"]').click()
        browser.find_element(by=By.XPATH, value='//*[@id="calendar-btn-search"]').click()
        solveCaptcha(browser)
        links = browser.find_elements(by=By.XPATH, value="//a[@href]")
        links = links[26:]
        linkArr = []
        for link in links:
            linkArr.append(link.get_attribute('href'))
        print("all %i links are stacked!" % (len(linkArr)))
        # linkArr = ['http://www.vologod.vybory.izbirkom.ru/region/izbirkom?action=show&root_a=1&vrn=4354028286341&region=35&global=&type=0&prver=0&pronetvd=null']
        for link in linkArr:
            # Кандидаты
            browser.get(link)
            solveCaptcha(browser)
            print(link)
            if os.path.exists(str("output/") + str(getParameterFromQuery(browser, "vrn")) + str(".json")):
                continue
            reports_name = browser.find_element(by=By.ID, value="standard-reports-name")

            if reports_name.is_displayed() is False:
                continue
            reports_name.click()
            solveCaptcha(browser)
            if browser.find_element(by=By.LINK_TEXT, value="Сведения о кандидатах"):
                browser.find_element(by=By.LINK_TEXT, value="Сведения о кандидатах").click()
            else:
                if browser.find_element(by=By.LINK_TEXT,
                                        value="Сведения о кандидатах, выдвинутых по одномандатным (многомандатным) избирательным округам"):
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
            current_json_vrn["level"] = level
            current_json_vrn["date"] = date_of_vote

            saveJson(current_json_vrn, str(current_json_vrn["vrn"]))
            goThroughUiks(browser, '/html/body/div[2]/main/div[2]/div[2]/div[1]/ul/li', raw_candidates)
        browser.get('http://www.vybory.izbirkom.ru/region/izbirkom')


if __name__ == '__main__':
    dates = sys.argv[1:]
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-blink-features=AutomationControlled")

    option.headless = not DEBUG
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
    browser.get('http://www.vybory.izbirkom.ru/region/izbirkom')
    observeData(browser, dates)
    browser.close()
