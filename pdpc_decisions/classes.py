import io
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict, List
from urllib.parse import urljoin

import bs4
import requests

logger = logging.getLogger(__name__)


class Options(TypedDict):
    csv_path: str
    download_folder: str
    corpus_folder: str
    action: str
    root: str
    extras: bool
    extra_corpus: bool


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


class Paragraph(object):
    def __init__(self, text: str, paragraph_mark: str = ''):
        self._text = text
        self._paragraph_mark = paragraph_mark

    @property
    def text(self):
        """Get the text of this paragraph."""
        return self._text

    @property
    def paragraph_mark(self):
        """Get the mark (paragraph number) of this paragraph, if available."""
        return self._paragraph_mark

    def update_text(self, new_text: str):
        self._text = new_text

    def __str__(self):
        if self._paragraph_mark:
            return f"Paragraph: {self._paragraph_mark} {self._text}"
        else:
            return f"Paragraph: NA, {self._text}"


class CorpusDocument:
    def __init__(self, source: PDPCDecisionItem = None):
        """
        Base document representing a PDPC Decision.
        :param source: (Optional) The decision which this document represents.
        """
        self.source = source
        self.paragraphs: List[Paragraph] = []

    def get_text_as_paragraphs(self, add_paragraph_marks: bool = False) -> List[str]:
        """
        Convenience method to get the text of the corpus_text as a list of string representing paragraphs.
        :param add_paragraph_marks: Paragraphs marks (such as paragraph numbers) are added to the front
        of the paragraph.
        :return:
        """
        result = []
        for paragraph in self.paragraphs:
            if add_paragraph_marks:
                result.append(f"{paragraph.paragraph_mark} {paragraph.text}")
            else:
                result.append(paragraph.text)
        return result

    def get_text(self, add_paragraph_marks: bool = False) -> str:
        """
        Convenience method to get the text of the corpus_text as string.
        :param add_paragraph_marks: Paragraphs marks (such as paragraph numbers) are added to the front
        of the paragraph.
        :return:
        """
        return " ".join(self.get_text_as_paragraphs(add_paragraph_marks))

    def add_paragraph(self, text: str, mark: str = ''):
        self.paragraphs.append(Paragraph(text, mark))

    def __iter__(self):
        return iter(self.paragraphs)

    def __str__(self):
        if self.source:
            return f"CorpusDocument:{len(self.paragraphs)}, source: {self.source.respondent}, " \
                   f"{self.source.published_date}"
        else:
            return f"CorpusDocument:{len(self.paragraphs)}, source: None"


class PDFFile:
    def __init__(self, source: PDPCDecisionItem, options: Options = None, *args, **kwargs):
        """
        A context manager to facilitate opening of PDF files. If a local file is found, that file is
        returned instead of downloading from the source.
        :param source:
        :param options:
        :param args:
        :param kwargs:
        """
        if options and ((options['action'] == 'all') or (options['action'] == 'files')):
            import os
            pdf_local_file_path = os.path.join(options['download_folder'],
                                               f"{source.published_date.strftime('%Y-%m-%d')} {source.respondent}.pdf")
            if os.path.isfile(pdf_local_file_path):
                logger.info('Using PDF file from local directory.')
                self.file_handler = open(pdf_local_file_path, 'rb')
                return
            if os.path.isfile(
                    os.path.join(options['download_folder'],
                                 f"{source.published_date.strftime('%Y-%m-%d')} {source.respondent} (1).pdf")):
                logger.warning(f'Returning a local file is not supported for secondary format. Source: {str(source)}')
        import requests
        r = requests.get(source.download_url)
        logger.info('Using PDF file from source.')
        self.file_handler = io.BytesIO(r.content)

    def __enter__(self):
        return self.file_handler

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_handler.close()
        return False
