#  MIT License Copyright (c) 2020. Houfu Ang
import io
from typing import List, Iterable

import requests
from pdfminer import layout
from pdfminer.high_level import extract_text_to_fp, extract_pages
from pdfminer.pdfpage import PDFPage

from scraper import PDPCDecisionItem


class Paragraph(object):
    _text: str = ''
    _paragraph_mark: str = ''

    @property
    def text(self):
        """Get the text of this paragraph."""
        return self._text

    @property
    def paragraph_mark(self):
        """Get the mark (paragraph number) of this paragraph, if available."""
        return self._paragraph_mark


class CorpusDocument:
    paragraphs: List[Paragraph] = []

    def get_text_as_paragraphs(self, add_paragraph_marks: bool = False) -> List[str]:
        """
        Convenience method to get the text of the corpus as a list of string representing paragraphs.
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
        Convenience method to get the text of the corpus as string.
        :param add_paragraph_marks: Paragraphs marks (such as paragraph numbers) are added to the front
        of the paragraph.
        :return:
        """
        return " ".join(self.get_text_as_paragraphs(add_paragraph_marks))

    def process_pages(self, pages: Iterable[layout.LTPage]):
        pass

    @classmethod
    def from_decision_item(cls, source: PDPCDecisionItem) -> 'CorpusDocument':
        result = cls()
        pdf = requests.get(source.download_url).content
        params = layout.LAParams(line_margin=2)
        if cls.check_first_page_is_cover(pdf):
            pages_count = len([page for page in PDFPage.get_pages(pdf)])
            pages = extract_pages(pdf, page_numbers=[i for i in range(pages_count)[1:]], laparams=params)
            result.process_pages([page for page in pages])
        else:
            pages = extract_pages(pdf, laparams=params)
            result.process_pages([page for page in pages])
        return result

    @staticmethod
    def check_first_page_is_cover(pdf: bytes) -> bool:
        with io.StringIO() as test_string:
            params = layout.LAParams(line_margin=2)
            extract_text_to_fp(pdf, test_string, page_numbers=[0], laparams=params)
            first_page = test_string.getvalue()
            return len(first_page.split()) <= 100
