#  MIT License Copyright (c) 2020. Houfu Ang

"""
Looks over the PDPC website and creates PDPC Decision objects

Requirements:
* Chrome Webdriver to automate web browser
"""
import logging
from typing import List

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from pdpc_decisions.classes import PDPCDecisionItem

logger = logging.getLogger(__name__)


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
