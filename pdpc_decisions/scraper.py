#  MIT License Copyright (c) 2019. Houfu Ang

"""
Looks over the PDPC website and creates PDPC Decision objects

Requirements:
* Chrome Webdriver to automate web browser
"""
import re
from datetime import datetime

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement


def refresh_pages(web_driver: Chrome):
    group_pages = web_driver.find_element_by_class_name('group__pages')
    return group_pages.find_elements_by_class_name('page-number')


def scrape():
    print('Setting up webdriver')
    # Setup webdriver
    options = Options()

    # Uncomment the next three lines for a headless chrome
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = Chrome(options=options)
    driver.implicitly_wait(5)
    result = []

    print('Starting the scrape')
    pdpc_decision_site_url = "https://www.pdpc.gov.sg/Commissions-Decisions/Data-Protection-Enforcement-Cases"
    try:
        driver.get(pdpc_decision_site_url)
        pages = refresh_pages(driver)
        for page_count in range(len(pages)):
            pages[page_count].click()
            print("Now at Page ", page_count)
            pages = refresh_pages(driver)
            decisions = driver.find_elements_by_class_name('press-item')
            for decision in decisions:
                item = PDPCDecisionItem(decision)
                print("Added:", item)
                result.append(item)
        print("No of items in result: ", len(result))
    finally:
        driver.close()
    print('Ending scrape.')
    return result


class PDPCDecisionItem:
    def __init__(self, decision: WebElement):
        self.decision = decision
        self.date = get_date(decision)
        self.respondent = get_respondent(decision)
        self.summary = get_summary(decision)
        self.download_url = get_url(decision)

    def __str__(self):
        return "PDPCDecision object: {} {}".format(self.date, self.respondent)


def get_date(item: WebElement):
    return datetime.strptime(item.find_element_by_class_name('press__date').text, "%d %b %Y")


def get_respondent(item: WebElement):
    link = item.find_element_by_tag_name('a')
    text = link.text
    return re.split(r"\s+[bB]y|[Aa]gainst\s+", text, re.I)[1].strip()


def get_url(item: WebElement):
    link = item.find_element_by_tag_name('a')
    return link.get_property('href')


def get_summary(item: WebElement):
    return item.find_element_by_class_name('rte').text.replace('\n', '. ')


if __name__ == '__main__':
    scrape()
