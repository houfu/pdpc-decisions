#  MIT License Copyright (c) 2020. Houfu Ang

"""
Looks over the PDPC website and creates PDPC Decision objects

Requirements:
* Chrome Webdriver to automate web browser
"""
import logging
import re
from dataclasses import dataclass
from datetime import datetime

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement


def get_url(item: WebElement):
    link = item.find_element_by_tag_name('a')
    return link.get_property('href')


def get_summary(item: WebElement):
    return item.find_element_by_class_name('rte').text.split('\n')[0]


def get_published_date(item: WebElement):
    return datetime.strptime(item.find_element_by_class_name('page-date').text, "%d %b %Y").date()


def get_respondent(item: WebElement):
    link = item.find_element_by_tag_name('h2')
    text = link.text
    return re.split(r"\s+[bB]y|[Aa]gainst\s+", text, re.I)[1].strip()


def get_title(item: WebElement):
    return item.find_element_by_class_name('page-title').text


class Scraper:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')

        self.driver = Chrome(options=options)
        self.driver.implicitly_wait(25)

    @classmethod
    def scrape(cls,
               site_url="https://www.pdpc.gov.sg/All-Commissions-Decisions?"
                        "keyword=&industry=all&nature=all&decision=all&penalty=all&page=1"):
        logging.info('Starting the scrape')
        self = cls()
        result = []
        try:
            self.driver.get(site_url)
            finished = False
            page_count = 1
            while not finished:
                items = self.driver.find_element_by_class_name('listing__list').find_elements_by_tag_name('li')
                for current_item in range(0, len(items)):
                    items = self.driver.find_element_by_class_name('listing__list').find_elements_by_tag_name('li')
                    from selenium.common.exceptions import NoSuchElementException
                    try:
                        items[current_item].click()
                        decision = self.driver.find_element_by_class_name('detail-content')
                        item = PDPCDecisionItem.from_element(decision)
                        logging.info('Added: {}, {}'.format(item.respondent, item.published_date))
                        result.append(item)
                        self.driver.back()
                    except NoSuchElementException:
                        logging.warning("'detail-content' was not found: {}".format(self.driver.current_url))
                next_page = self.driver.find_element_by_class_name('pagination-next')
                if 'disabled' in next_page.get_attribute('class'):
                    finished = True
                else:
                    page_count += 1
                    new_url = "https://www.pdpc.gov.sg/All-Commissions-Decisions?page={}".format(page_count)
                    self.driver.get(new_url)
        finally:
            self.driver.close()
        logging.info('Ending scrape.')
        return result


@dataclass
class PDPCDecisionItem:
    published_date: datetime.date
    respondent: str
    title: str
    summary: str
    download_url: str

    @classmethod
    def from_element(cls, decision: WebElement):
        published_date = get_published_date(decision)
        respondent = get_respondent(decision)
        title = get_title(decision)
        summary = get_summary(decision)
        download_url = get_url(decision)
        return cls(published_date, respondent, title, summary, download_url)

    def __str__(self):
        return "PDPCDecision object: {} {}".format(self.published_date, self.respondent)
