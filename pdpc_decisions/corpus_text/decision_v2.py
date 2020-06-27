import logging
import re
from typing import List, Dict, Optional

from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LAParams, LTTextBoxHorizontal, LTTextLineHorizontal, LTChar

from pdpc_decisions.classes import PDPCDecisionItem, Options, PDFFile
from pdpc_decisions.corpus_text import common
from pdpc_decisions.corpus_text.common import BaseCorpusDocumentFactory

logger = logging.getLogger(__name__)


def check_next_footnote(footnotes, index):
    if not len(footnotes) == index + 1:
        next_footnote = footnotes[index + 1]
    else:
        return False
    if re.match(r'\d+\s*', next_footnote.get_text().strip()):
        if isinstance(next_footnote, LTTextBoxHorizontal):
            first_char = next(iter(next(iter(next_footnote))))
        elif isinstance(next_footnote, LTTextLineHorizontal):
            first_char = next(iter(next_footnote))
        else:
            return False
        if round(first_char.height) < common.get_main_text_size([next_footnote]):
            return True
        else:
            return False


class DecisionV2Factory(BaseCorpusDocumentFactory):
    def __init__(self, **kwargs):
        super(DecisionV2Factory, self).__init__(laparams=LAParams(line_margin=0.5), **kwargs)
        self._common_font = ''
        self._paragraph_marks = []
        self._text_margins = [72]
        self._paragraph_strings: List[str] = []
        self._current_paragraph_mark = ''
        self._main_text_size = 12
        self._footnotes: Dict[str, str] = dict()

    def _extract_pages_and_text_containers(self, pdf):
        self._pages = list(extract_pages(pdf, laparams=self.data.get('laparams', None)))[1:]
        for page in self._pages:
            self._text_containers.append([element for element in page if
                                          isinstance(element, LTTextContainer) and
                                          element.get_text() != '' and not
                                          re.search(r'^\s+$', element.get_text())])

    def pre_process(self):
        BaseCorpusDocumentFactory.pre_process(self)
        self._common_font = common.get_common_font_from_pages(self._pages)
        margin_limit = 3 if len(self._pages) > 3 else len(self._pages)
        self._text_margins = common.get_text_margins(list(self.get_text_containers()), margin_limit)
        self._main_text_size = common.get_main_text_size(list(self.get_text_containers()))
        for index, containers in enumerate(self._text_containers):
            containers = common.split_joined_text_containers(containers)
            containers = [container for container in containers if all([
                container.get_text().strip() != '',
                round(container.x0) in self._text_margins,
                round(container.height) <= self._main_text_size + 1 or self._check_footnote(container)
            ])]
            containers = sorted(containers, key=lambda item: item.x0)
            containers = sorted(containers, key=lambda item: item.y0, reverse=True)
            self._text_containers[index] = containers
        self._footnotes = self._get_and_remove_footnotes()
        logger.info("Pre process finished.")

    def _get_and_remove_footnotes(self):
        footnotes = []
        for index, page in enumerate(self._pages):
            new_containers, footnote_page = common.get_footnotes_using_separator(page,
                                                                                 self._text_containers[index],
                                                                                 self._text_margins[0],
                                                                                 self._main_text_size)
            self._text_containers[index] = new_containers
            if footnote_page:
                footnotes.extend(footnote_page)
        return common.construct_footnotes(footnotes)

    def process_all(self):
        for index, page_containers in enumerate(self._text_containers):
            self.process_page(page_containers)

    def process_paragraph(self, paragraph: LTTextContainer, index: int, page_containers: List[LTTextContainer]) -> None:
        logger.info(f"New container: {paragraph}")
        if self._check_skip_paragraph(paragraph, index):
            return
        container_string = self._replace_footnote(paragraph)
        container_string = self._check_top_paragraph(container_string, paragraph)
        self._paragraph_strings.append(container_string)
        logger.info(f'Added to paragraph strings')
        self._check_paragraph_end(index, page_containers)
        logger.info("End of this container.")

    def _check_footnote(self, paragraph):
        result = []
        char_text = []
        if isinstance(paragraph, LTTextBoxHorizontal):
            char_list = list(iter(next(iter(paragraph))))
        elif isinstance(paragraph, LTTextLineHorizontal):
            char_list = list(iter(paragraph))
        else:
            return None
        for index, char in enumerate(char_list):
            if isinstance(char, LTChar) and round(char.height) < self._main_text_size and \
                    re.match(r'\d', char.get_text()):
                char_text.append(char.get_text())
                if (index + 1 == len(char_list)) or (isinstance(char_list[index + 1], LTChar) and round(
                        char_list[index + 1].height) >= self._main_text_size):
                    footnote_mark = ''.join(char_text)
                    result.append(footnote_mark)
                    char_text.clear()
        return result if len(result) > 0 else None

    def _replace_footnote(self, paragraph):
        result = paragraph.get_text().strip()
        if footnotes_marks := self._check_footnote(paragraph):
            for footnote_mark in footnotes_marks:
                if self._footnotes.get(footnote_mark):
                    result = result.replace(footnote_mark, f" ({self._footnotes[footnote_mark]})", 1)
                    logger.info(f'Replaced a footnote: {footnote_mark}, {self._footnotes[footnote_mark]}')
                else:
                    logger.warning(f'Footnote mark ({footnote_mark}) cannot be replaced as it is not in the footnotes.')
        return result

    def _check_top_paragraph(self, container_string, paragraph):
        if all([
            round(paragraph.x0) == self._text_margins[0],
            match := re.match(r'\d+\.?\s*', paragraph.get_text()),
            not self._current_paragraph_mark
        ]):
            self._current_paragraph_mark = match.group(0).strip()
            logger.info(f"Added a paragraph mark: {self._current_paragraph_mark}")
            container_string = container_string.replace(self._current_paragraph_mark, '', 1)
            logger.info(f"Adjust container: {container_string}")
        return container_string

    def _check_paragraph_end(self, index, page_containers):
        if all([common.check_gap_before_after_container(page_containers, index, equal=True),
                not common.check_common_font(page_containers[index], self._common_font),
                not self._current_paragraph_mark
                ]):
            self._result.add_paragraph(" ".join(self._paragraph_strings))
            logger.info(f'Added a header-like paragraph: {self._result.paragraphs[-1].text}')
            self._paragraph_strings.clear()
            return
        if re.search(r'[.?!][")]?\d*\s*$', page_containers[index].get_text()) and any([
            len(self._paragraph_strings) == 1,
            common.check_gap_before_after_container(page_containers, index)
        ]):
            if self._current_paragraph_mark:
                self._result.add_paragraph(" ".join(self._paragraph_strings), self._current_paragraph_mark)
            else:
                logger.warning(
                    f'No paragraph mark was found for ({self._paragraph_strings[0]}).')
                if len(self._result.paragraphs) > 0:
                    logger.info('Adding to previous parargraph')
                    self._paragraph_strings.insert(0, self._result.paragraphs[-1].text)
                    self._result.paragraphs[-1].update_text(" ".join(self._paragraph_strings))
                else:
                    logger.warning('Creating a new paragraph')
                    self._result.add_paragraph(" ".join(self._paragraph_strings))
            logger.info(f'Added a paragraph: {self._result.paragraphs[-1]}')
            self._paragraph_strings.clear()
            self._current_paragraph_mark = ''
            logger.info('Reset paragraph mark and string.')

    def _check_skip_paragraph(self, paragraph, index):
        paragraph_text = paragraph.get_text().strip()
        if common.check_text_is_date(paragraph):
            logger.info('Date found, skipping')
            return True
        if any([
            re.match(r'[A-Z ]+\s*$', paragraph_text),
            re.match(r'(\[\d{4}])\s+((?:\d\s+)?[A-Z|()]+)\s+\[?(\d+)\]?', paragraph_text),
            re.match(r'Tan Kiat How', paragraph_text),
            re.match(r'Yeong Zee Kin', paragraph_text)
        ]):
            logger.info('Meta-info found, skipping')
            return True
        if index == 0 and len(self._pages) > 1:
            if paragraph_text == self._text_containers[1][0].get_text().strip():
                logger.info('Looks like a header. Skipping.')
                return True
        if round(paragraph.y0) > 700 and re.match(r'(\[\d{4}])\s+((?:\d\s+)?[A-Z|()]+)\s+\[?(\d+)\]?', paragraph_text):
            logger.info('Looks like a header. Skipping.')
            return True
        if 284 < round(paragraph.x0) < 296 and re.match(r'\d+$', paragraph_text):
            logger.info('Looks like a footer. Skipping.')
            return True
        if re.match(r'\d+ of \d+$', paragraph_text):
            logger.info('Looks like a footer. Skipping.')
            return True
        return False

    @classmethod
    def check_decision(cls, item: Optional[PDPCDecisionItem] = None, options: Optional[Options] = None) -> bool:
        with PDFFile(item, options) as pdf:
            first_page = extract_pages(pdf, page_numbers=[0], laparams=LAParams(line_margin=0.1, char_margin=3.5))
            text = extract_text(pdf, page_numbers=[0], laparams=LAParams(line_margin=0.1, char_margin=3.5))
            containers = common.extract_text_containers(first_page)
            if len(text.split()) <= 100:
                for container in containers:
                    container_text = container.get_text().strip()
                    if container_text == 'DECISION' or container_text == 'GROUNDS OF DECISION':
                        return True
        return False
