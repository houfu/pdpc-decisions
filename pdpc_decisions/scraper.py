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
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)


def get_url(article: Tag, url: str) -> str:
    """Gets the URL for the text of the decision."""
    link = article.find('a')
    return urljoin(url, link['href'])


def get_summary(article: Tag) -> str:
    """Gets the summary of a decision as provided by the PDPC."""
    paragraphs = article.find(class_='rte').find_all('p')
    result = ''
    for paragraph in paragraphs:
        if not paragraph.text == '':
            result += paragraph.text
            break
    return result


def get_published_date(article: Tag) -> datetime.date:
    """Gets the date when the decision is published on the PDPC Website"""
    return datetime.strptime(article.find(class_='page-date').text, "%d %b %Y").date()


def get_respondent(article: Tag) -> str:
    """Gets the name of the respondent in the decision from title of the decision."""
    return re.split(r"\s+[bB]y|[Aa]gainst\s+", article.find('h2').text, re.I)[1].strip()


def get_title(article: Tag) -> str:
    """Gets the title of the decision as provided by the PDPC"""
    return article.find('h2').text


@dataclass
class PDPCDecisionItem:
    published_date: datetime.date
    respondent: str
    title: str
    summary: str
    download_url: str

    @classmethod
    def from_web_page(cls, decision: str):
        """
        Create a PDPCDecisionItem from a section in the PDPC Website's list of commission's decisions.
        :param decision:
        :return:
        """
        soup = BeautifulSoup(requests.get(decision).text, features='html5lib')
        article = soup.find('article')
        published_date = get_published_date(article)
        respondent = get_respondent(article)
        title = get_title(article)
        summary = get_summary(article)
        download_url = get_url(article, decision)
        return cls(published_date, respondent, title, summary, download_url)

    def __str__(self):
        return f"PDPCDecisionItem: {self.published_date} {self.respondent}"


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
                        "keyword=&industry=all&nature=all&decision=all&penalty=all&page=1") -> List[PDPCDecisionItem]:
        """Convenience method for scraping the PDPC Decision website with Scraper."""
        logger.info('Starting the scrape')
        self = cls()
        result = []
        try:
            self.driver.get(site_url)
            finished = False
            page_count = 1
            logger.info('Now at page 1.')
            while not finished:
                items = self.driver.find_element_by_class_name('listing__list').find_elements_by_tag_name('li')
                for current_item in range(0, len(items)):
                    items = self.driver.find_element_by_class_name('listing__list').find_elements_by_tag_name('li')
                    link = items[current_item].find_element_by_tag_name('a').get_property('href')
                    item = PDPCDecisionItem.from_web_page(link)
                    logger.info(f'Added: {item.respondent}, {item.published_date}')
                    result.append(item)
                next_page = self.driver.find_element_by_class_name('pagination-next')
                if 'disabled' in next_page.get_attribute('class'):
                    logger.info('Scraper has reached end of page.')
                    finished = True
                else:
                    page_count += 1
                    new_url = "https://www.pdpc.gov.sg/All-Commissions-Decisions?page={}".format(page_count)
                    self.driver.get(new_url)
                    logger.info(f'Now at page {page_count}')
        finally:
            self.driver.close()
        logger.info(f'Ending scrape with {len(result)} items.')
        return result
