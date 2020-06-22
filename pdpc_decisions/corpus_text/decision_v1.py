import logging
import re
from typing import Generator, Tuple, List, Dict, Optional

from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer, LTRect, LTChar, LTTextBoxHorizontal, LTTextLineHorizontal

import pdpc_decisions.classes
import pdpc_decisions.corpus_text.common as common
from pdpc_decisions.classes import PDPCDecisionItem, Options

logger = logging.getLogger(__name__)


class DecisionV1Factory(common.BaseCorpusDocumentFactory):
    def __init__(self, **kwargs):
        super().__init__(laparams=LAParams(line_margin=0.1, char_margin=3.5), **kwargs)
        self._custom_text_containers: List[List[LTTextContainer]] = []
        self._paragraph_marks = []
        self._text_margins = [72]
        self._paragraph_strings: List[str] = []
        self._assigned_marks = []
        self._current_paragraph_mark = ''
        self._main_text_size = 12
        self._footnotes: Dict[str, str] = dict()

    def _extract_pages_and_text_containers(self, pdf):
        self._pages = list(extract_pages(pdf, laparams=self.data.get('laparams', None)))
        for page in self._pages:
            self._text_containers.append([element for element in page if
                                          isinstance(element, LTTextContainer) and all([
                                              element.get_text().strip() != '',
                                              # common.check_common_font(element, 'Arial'),
                                          ])])

    def pre_process(self):
        common.BaseCorpusDocumentFactory.pre_process(self)
        self._text_margins = common.get_text_margins(
            list(self.get_text_containers()), len(self._pages))
        self._get_custom_text_containers()
        self._main_text_size = common.get_main_text_size(
            list(self.get_text_containers(custom_container=self._custom_text_containers)))
        self._paragraph_marks = list(self._get_paragraph_marks())
        self._footnotes = self._get_and_remove_footnotes()

    def _get_custom_text_containers(self):
        logger.info('Preparing filtered text containers')
        self._custom_text_containers.clear()
        for index, page_containers in enumerate(self._text_containers):
            page_containers = [container for container in page_containers if
                               round(container.x0) in self._text_margins]
            page_containers = common.split_joined_text_containers(page_containers)
            page_containers = self._remove_underlined_headers_from_page(page_containers, index)
            page_containers = sorted(page_containers, key=lambda item: item.x0)
            page_containers = sorted(page_containers, key=lambda container: container.y0, reverse=True)
            self._custom_text_containers.append(page_containers)

    def _remove_underlined_headers_from_page(self, page_containers, index):
        underlined_headers = [element for element in self._pages[index] if isinstance(element, LTRect)
                              and round(element.x0) == self._text_margins[0]]
        page_containers_result = page_containers.copy()
        for header in underlined_headers:
            for container in page_containers:
                if container.y0 < header.y0 <= container.y1 and container.get_text().strip() != '':
                    logger.info(f'Found an underlined header: {container.get_text()}')
                    page_containers_result.remove(container)
        return page_containers_result

    def _get_paragraph_marks(self) -> Generator[Tuple[LTTextContainer, LTTextContainer], None, None]:
        for page_containers in self._custom_text_containers:
            paragraph_marks = [container for container in page_containers
                               if container.width < 30 and round(container.x0) == self._text_margins[0]
                               and re.match(r'\w+\.\s', container.get_text())]
            for mark in paragraph_marks:
                page_containers.remove(mark)
                match = next(container for container in page_containers if
                             common.is_on_the_same_line(container, mark))
                logger.info(f"Stray paragraph mark found: {match}, {mark}")
                yield match, mark

    def _get_and_remove_footnotes(self) -> Dict[str, str]:
        footnotes = []
        search_list = self.get_text_containers(custom_container=self._custom_text_containers)
        for container in search_list:
            if round(container.height) < self._main_text_size and container.get_text().strip() != '':
                footnotes.append(container)
        result = []
        footnote_text = []
        for container in footnotes:
            footnote_string = container.get_text().strip()
            footnote_text.append(footnote_string)
            if re.search(r'[.?!]\s*$', footnote_string):
                footnote_mark = re.match(r'\d\s+', footnote_text[0]).group(0).strip()
                footnote = ' '.join(footnote_text).replace(footnote_mark, '', 1).strip()
                result.append((footnote_mark, footnote))
                logger.info(f"Found a footnote: ({footnote_mark}, {footnote})")
                footnote_text.clear()
        for index, page in enumerate(self._custom_text_containers):
            self._custom_text_containers[index] = [container for container in self._custom_text_containers[index] if
                                                   container not in footnotes]
        return dict(result)

    def process_all(self):
        for index, page_containers in enumerate(self._custom_text_containers):
            self.process_page(page_containers)

    def process_paragraph(self, paragraph, index, page_containers):
        logger.info(f"New container: {paragraph}")
        if common.check_text_is_date(paragraph):
            logger.info('Date found, skipping')
            return
        if not common.check_common_font(paragraph, 'Arial') and any([
            round(paragraph.x0) == self._text_margins[0],
            paragraph.get_text().isupper()
        ]):
            logger.info('Skipping header')
            return
        container_string = self._replace_footnote(paragraph)
        container_string = self._check_top_paragraph(container_string, paragraph)
        self._paragraph_strings.append(container_string)
        logger.info(f'Added to paragraph strings')
        self._check_paragraph_end(container_string, index, page_containers)
        logger.info("End of this container.")

    def _check_paragraph_end(self, container_string, index, page_containers):
        if re.search(r'[.?!]\s*$', container_string) and (
                len(self._paragraph_strings) == 1 or common.check_gap_before_after_container(page_containers, index,
                                                                                             equal=True)):
            if not self._current_paragraph_mark:
                logger.info('This paragraph has no mark. Look for stray marks.')
                mark_match = 'start'
                while mark_match not in self._assigned_marks:
                    mark_match = next((mark.get_text().strip() for match, mark in self._paragraph_marks
                                       if match.get_text().strip() == self._paragraph_strings[0]), None)
                    if mark_match is None:
                        logger.warning(f'No paragraph mark was found for "{self._paragraph_strings[0]}". '
                                       f'A paragraph will be created anyway.')
                        self._current_paragraph_mark = None
                    if mark_match not in self._assigned_marks:
                        self._current_paragraph_mark = mark_match
                        logger.info(f'Found a mark: {self._current_paragraph_mark}')
                        self._assigned_marks.append(mark_match)
            if self._current_paragraph_mark:
                self._result.add_paragraph(" ".join(self._paragraph_strings), self._current_paragraph_mark)
                logger.info(f'Added a paragraph: {" ".join(self._paragraph_strings)}')
            else:
                self._paragraph_strings.insert(0, self._result.paragraphs[-1].text)
                self._result.paragraphs[-1].update_text(" ".join(self._paragraph_strings))
                logger.info(f'Added a paragraph: {" ".join(self._paragraph_strings)}')
            self._paragraph_strings.clear()
            self._current_paragraph_mark = ''
            logger.info('Reset paragraph mark and string.')

    def _check_top_paragraph(self, container_string, paragraph):
        if paragraph.width > 200 and round(paragraph.x0) == self._text_margins[0]:
            match = re.match(r'\w+\.\s', container_string)
            if match:
                self._current_paragraph_mark = match.group(0).strip()
                logger.info(f"Added a paragraph mark: {self._current_paragraph_mark}")
                container_string = container_string.replace(self._current_paragraph_mark, '', 1).strip()
                logger.info(f"Adjust container: {container_string}")
            else:
                logger.warning(f'No paragraph mark was found: {paragraph.get_text().strip()}')
        return container_string

    def _replace_footnote(self, container):
        char_text = []
        result = container.get_text().strip()
        if isinstance(container, LTTextBoxHorizontal):
            char_list = list(iter(next(iter(container))))
        elif isinstance(container, LTTextLineHorizontal):
            char_list = list(iter(container))
        else:
            return result
        for index, char in enumerate(char_list):
            if isinstance(char, LTChar) and round(char.height) < self._main_text_size and re.match(r'\d',
                                                                                                   char.get_text()):
                char_text.append(char.get_text())
                if isinstance(char_list[index + 1], LTChar) and \
                        round(char_list[index + 1].height) >= self._main_text_size:
                    footnote_mark = ''.join(char_text)
                    result = result.replace(footnote_mark, f" ({self._footnotes[footnote_mark]})", 1)
                    logger.info(f'Replaced a footnote: {footnote_mark}, {self._footnotes[footnote_mark]}')
        return result

    @classmethod
    def check_decision(cls, item: Optional[PDPCDecisionItem] = None, options: Optional[Options] = None) -> bool:
        with pdpc_decisions.classes.PDFFile(item, options) as pdf:
            first_page = extract_pages(pdf, page_numbers=[0], laparams=LAParams(line_margin=0.1, char_margin=3.5))
            containers = common.extract_text_containers(first_page)
            for container in containers:
                font, is_only = common.get_common_font_from_paragraph(container)
                if container.get_text().strip() == 'GROUNDS OF DECISION' and font == 'Arial,Bold' and is_only:
                    return True
        return False
