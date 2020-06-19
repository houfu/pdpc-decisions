import logging
import re
from typing import List, Dict, Optional

from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LAParams, LTTextBoxHorizontal, LTTextLineHorizontal, LTChar, LTRect

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
        self._text_margins = common.get_text_margins(list(self.get_text_containers()), len(self._pages))
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
            if footnote_line_container := [container for container in page if all([
                isinstance(container, LTRect),
                container.height < 1,
                container.y0 < 350,
                container.width < 150,
                round(container.x0) == self._text_margins[0]
            ])]:
                footnote_line_container = sorted(footnote_line_container, key=lambda container: container.y0)
                footnote_line = footnote_line_container[0].y0
                footnotes_page = [container for container in self._text_containers[index] if
                                  container.y0 < footnote_line]
                footnotes.extend(footnotes_page)
                self._text_containers[index] = [container for container in self._text_containers[index] if
                                                container not in footnotes_page]
        result = []
        footnote_text = []
        for index, footnote in enumerate(footnotes):
            footnote_string = footnote.get_text().strip()
            footnote_text.append(footnote_string)
            if any([re.search(r'[.?!)\]]\s*$', footnote_string),
                    check_next_footnote(footnotes, index),
                    len(footnotes) == index + 1
                    ]):
                match = re.match(r'\d+\s*', footnote_text[0])
                if match:
                    footnote_mark = match.group(0).strip()
                    footnote = ' '.join(footnote_text).replace(footnote_mark, '', 1).strip()
                    result.append((footnote_mark, footnote))
                    logger.info(f"Found a footnote: ({footnote_mark}, {footnote})")
                else:
                    logger.warning(f'No footnote mark found: {footnote_string}, appending to the last footnote.')
                    footnote_text.insert(0, result[-1][1])
                    footnote = ' '.join(footnote_text).strip()
                    result[-1] = (result[-1][0], footnote)
                footnote_text.clear()
        return dict(result)

    def process_all(self):
        for index, page_containers in enumerate(self._text_containers):
            self.process_page(page_containers)

    def process_paragraph(self, paragraph: LTTextContainer, index: int, page_containers: List[LTTextContainer]) -> None:
        logger.info(f"New container: {paragraph}")
        if common.check_text_is_date(paragraph):
            logger.info('Date found, skipping')
            return
        if any([
            re.match(r'[A-Z ]+\s*$', paragraph.get_text()),
            re.match(r'Tan Kiat How', paragraph.get_text()),
            re.match(r'Yeong Zee Kin', paragraph.get_text())
        ]):
            logger.info('Meta-info found, skipping')
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
                if isinstance(char_list[index + 1], LTChar) and round(
                        char_list[index + 1].height) >= self._main_text_size:
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
            match := re.match(r'\d+.?\s*', paragraph.get_text()),
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
        if re.search(r'[.?!]"?\d*\s*$', page_containers[index].get_text()) and any([
            len(self._paragraph_strings) == 1,
            common.check_gap_before_after_container(page_containers, index)
        ]):
            if self._current_paragraph_mark:
                self._result.add_paragraph(" ".join(self._paragraph_strings), self._current_paragraph_mark)
            else:
                logger.warning(
                    f'No paragraph mark was found for ({self._paragraph_strings[0]}). Adding to previous paragraph.')
                self._paragraph_strings.insert(0, self._result.paragraphs[-1].text)
                self._result.paragraphs[-1].update_text(" ".join(self._paragraph_strings))
            logger.info(f'Added a paragraph: {self._result.paragraphs[-1]}')
            self._paragraph_strings.clear()
            self._current_paragraph_mark = ''
            logger.info('Reset paragraph mark and string.')

    @classmethod
    def check_decision(cls, item: Optional[PDPCDecisionItem] = None, options: Optional[Options] = None) -> bool:
        with PDFFile(item, options) as pdf:
            first_page = extract_pages(pdf, page_numbers=[0], laparams=LAParams(line_margin=0.1, char_margin=3.5))
            text = extract_text(pdf, page_numbers=[0], laparams=LAParams(line_margin=0.1, char_margin=3.5))
            containers = common.extract_text_containers(first_page)
            if len(text.split()) <= 100:
                for container in containers:
                    if container.get_text().strip() == 'DECISION':
                        return True
        return False
