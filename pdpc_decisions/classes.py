import re
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict
from urllib.parse import urljoin

import bs4
import requests


class Options(TypedDict):
    csv_path: str
    download_folder: str
    corpus_folder: str
    action: str
    root: str
    extras: bool


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
        :param decision: Link to PDPC's decision page.
        :return:
        """
        soup = bs4.BeautifulSoup(requests.get(decision).text, features='html5lib')
        article = soup.find('article')
        published_date = cls.get_published_date(article)
        respondent = cls.get_respondent(article)
        title = cls.get_title(article)
        summary = cls.get_summary(article)
        download_url = cls.get_url(article, decision)
        return cls(published_date, respondent, title, summary, download_url)

    @staticmethod
    def get_url(article: bs4.Tag, url: str) -> str:
        """Gets the URL for the text of the decision."""
        link = article.find('a')
        return urljoin(url, link['href'])

    @staticmethod
    def get_summary(article: bs4.Tag) -> str:
        """Gets the summary of a decision as provided by the PDPC."""
        paragraphs = article.find(class_='rte').find_all('p')
        result = ''
        for paragraph in paragraphs:
            if not paragraph.text == '':
                result += re.sub(r'\s+', ' ', paragraph.text)
                break
        return result

    @staticmethod
    def get_published_date(article: bs4.Tag) -> datetime.date:
        """Gets the date when the decision is published on the PDPC Website"""
        return datetime.strptime(article.find(class_='page-date').text, "%d %b %Y").date()

    @staticmethod
    def get_respondent(article: bs4.Tag) -> str:
        """Gets the name of the respondent in the decision from title of the decision."""
        text = re.split(r"\s+[bB]y|[Aa]gainst\s+", article.find('h2').text, re.I)[1].strip()
        return re.sub(r'\s+', ' ', text)

    @staticmethod
    def get_title(article: bs4.Tag) -> str:
        """Gets the title of the decision as provided by the PDPC"""
        return re.sub(r'\s+', ' ', article.find('h2').text)

    def __str__(self):
        return f"PDPCDecisionItem: {self.published_date} {self.respondent}"
