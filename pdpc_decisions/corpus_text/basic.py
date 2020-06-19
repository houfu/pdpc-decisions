import logging
import re
from typing import List

from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer

import pdpc_decisions.corpus_text.common as common
from pdpc_decisions.corpus_text.common import BaseCorpusDocumentFactory

logger = logging.getLogger(__name__)


class BasicCorpusFactory(BaseCorpusDocumentFactory):
    """
    Basic factory for CorpusDocument with the aim of producing results similar to previous
    versions of pdpc-decisions, with a focus on non-destructive rendering of documents
    and ensuring that a CorpusDocument is produced with no exceptions.
    """

    def __init__(self, **kwargs):
        super().__init__(laparams=LAParams(line_margin=2), **kwargs)
        self._paragraph_strings: List[str] = []

    def _extract_pages_and_text_containers(self, pdf):
        self._pages = list(extract_pages(pdf, laparams=self.data.get('laparams', None)))
        if common.check_first_page_is_cover(pdf):
            self._pages = self._pages[1:]
        for page in self._pages:
            containers = [element for element in page if isinstance(element, LTTextContainer) and
                          element.get_text() != '' and not
                          re.search(r'^\s+$', element.get_text())]
            containers = common.split_joined_text_containers(containers)
            containers = sorted(containers, key=lambda item: item.x0)
            containers = sorted(containers, key=lambda item: item.y0, reverse=True)
            self._text_containers.append(containers)

    def process_paragraph(self, paragraph, index, page_containers):
        logger.info(f"New container: {paragraph}")
        text = paragraph.get_text().strip()
        if common.check_text_is_date(paragraph):
            logger.info('Date found, skipping')
            return
        if re.search(r'^\s+\[\d{4}]\s+(?:\d\s+)?[A-Z|()]+\s+\d+[\s.]?\s+$', text):
            logger.info('Citation found, skipping')
            return
        if re.search(r'^\d*[\s.]*$', text):
            logger.info('Number found, skipping')
            return
        self._paragraph_strings.append(text)
        logger.info(f'Added to paragraph strings')
        self._check_paragraph_end()
        logger.info("End of this container.")

    def _check_paragraph_end(self):
        text = self._paragraph_strings[-1]
        if re.search(r'\.\s*$', text):
            self._result.add_paragraph(' '.join(self._paragraph_strings))
            logger.info(f'Added a paragraph: {self._result.paragraphs[-1]}')
            self._paragraph_strings.clear()
