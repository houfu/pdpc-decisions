import io
import logging
import re
from collections import Counter
from typing import List, Generator, Dict, Optional

from pdfminer import layout
from pdfminer.high_level import extract_text_to_fp, extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTPage, LTTextLineHorizontal, LTRect

from pdpc_decisions.classes import Options, PDPCDecisionItem, CorpusDocument, PDFFile

logger = logging.getLogger(__name__)


def check_text_is_date(paragraph: LTTextContainer) -> bool:
    """Returns true if the text of a paragraph contains only a date."""
    return re.match(r'\d\d? \w+ \d\d\d\d\s*$', paragraph.get_text().strip()) is not None


def get_text_margins(text_containers: List[LTTextContainer], limit: int = 1) -> List[int]:
    """
    Returns a list of integers (from left to right) representing the most commonly used text
    margins in a document.

    :param limit: If there are any margins with counts less than limit, it is removed.
    :param text_containers: The document to evaluate.
    :return: A list of rounded integers.
    """
    containers_x0 = [round(container.x0) for container in text_containers]
    c = Counter(containers_x0)
    logger.info(f"Text margins: {c}")
    return sorted([margin for margin, count in c.most_common() if count > limit])


def get_main_text_size(text_containers: List[LTTextContainer]) -> int:
    """Returns the text size in points of the most common text in text containers."""
    font_sizes = [container.height for container in text_containers]
    c = Counter(font_sizes)
    size, _ = c.most_common(1)[0]
    return round(size)


def check_first_page_is_cover(pdf: bytes) -> bool:
    """Reads pdf and returns True if it is a cover page"""
    with io.StringIO() as test_string:
        params = layout.LAParams(line_margin=2)
        extract_text_to_fp(pdf, test_string, page_numbers=[0], laparams=params)
        first_page = test_string.getvalue()
        return len(first_page.split()) <= 100


def get_common_font_from_pages(pages: List[LTPage]) -> str:
    """Gets the most common font from a list of pages and return its name"""
    font_names = []
    text_containers = extract_text_containers((page for page in pages))
    for container in text_containers:
        for line in container:
            for char in line:
                if isinstance(char, layout.LTChar):
                    font_names.append(char.fontname)
    c = Counter(font_names)
    font, _ = c.most_common(1)[0]
    return font


def get_common_font_from_paragraph(paragraph: layout.LTTextContainer) -> (str, bool):
    """
    Get the most common font in a paragraph text.

    :param paragraph: The text container to evaluate.
    :return: A tuple of type (str, bool) stating the name of the most common font, and
             whether it is the only font in the paragraph.
    """
    fonts = []
    if isinstance(paragraph, LTTextLineHorizontal):
        fonts.extend([char.fontname for char in paragraph if isinstance(char, LTChar)])
    else:
        for line in paragraph:
            fonts.extend([char.fontname for char in line if isinstance(char, layout.LTChar)])
    c = Counter(fonts)
    font, _ = c.most_common(1)[0]
    return font, len(c) == 1


def check_common_font(paragraph: layout.LTTextContainer, common_font: str) -> bool:
    """Returns true if the most common font in paragraph is common font, or if common
    font is one of the fonts used in the paragraph. """
    fonts = []
    if isinstance(paragraph, LTTextLineHorizontal):
        fonts.extend([char.fontname for char in paragraph if isinstance(char, LTChar)])
    else:
        for line in paragraph:
            fonts.extend([char.fontname for char in line if isinstance(char, LTChar)])
    c = Counter(fonts)
    font, _ = c.most_common(1)[0]
    return common_font == font or common_font in c


def check_gap_before_after_container(containers: List[LTTextContainer], index: int, equal=False) -> bool:
    """Returns true if the gap before the container is smaller than the gap after.
    Tries to check for the next container if there are two on the same line, or if it is the last
    container of a page."""
    index_before = index - 1
    while not index_before < 0 and containers[index].y0 == containers[index_before].y0:
        index_before -= 1
    if index_before < 0:
        return False
    index_after = index + 1
    while not index_after >= len(containers) and containers[index].y0 == containers[index_after].y0:
        index_after += 1
    if index_after == len(containers):
        return True
    gap_before = round(containers[index_before].y1 - containers[index].y0)
    gap_after = round(containers[index].y1 - containers[index_after].y0)
    if equal:
        return gap_after >= gap_before
    else:
        return gap_after > gap_before


def is_on_the_same_line(paragraph_1: layout.LTTextContainer, paragraph_2: layout.LTTextContainer) -> bool:
    """Returns true if paragraph 1 and paragraph 2 are on the same line."""
    return paragraph_1.y1 == paragraph_2.y1 and not paragraph_1.get_text() == paragraph_2.get_text()


def extract_text_containers(pages: Generator[layout.LTPage, None, None]) -> List[layout.LTTextContainer]:
    result = []
    for page in pages:
        result.extend([element for element in page if
                       isinstance(element, layout.LTTextContainer) and element.get_text() != '' and not re.search(
                           r'^\s+$', element.get_text())])
    return result


def split_joined_text_containers(containers: List[LTTextContainer]) -> List[LTTextContainer]:
    """Searches for text containers in individual containers, splits them and returns the result."""
    result = containers.copy()
    container_length = len(containers) - 1
    logger.info(f'Start splitting containers in reverse fashion.')
    for index in range(container_length, -1, -1):
        container = containers[index]
        if len(container) > 1:
            new_item = []
            for sub_container in container:
                if isinstance(sub_container, LTTextContainer) and sub_container.get_text().strip() != '':
                    logger.info(f'Found split container: {sub_container}')
                    new_item.append(sub_container)
            if len(new_item) != 0:
                result.remove(container)
                result[index:index] = new_item
                logger.info(f'Splitting joined container.')
    return result


def get_footnotes_using_separator(page: LTPage, text_containers: List[LTTextContainer],
                                  left_margin: int, main_text_size: int) \
        -> (List[LTTextContainer], Optional[List[LTTextContainer]]):
    if footnote_line_container := [container for container in page if all([
        isinstance(container, LTRect),
        container.height < 1,
        container.y0 < 350,
        container.width < 150,
        round(container.x0) == left_margin
    ])]:
        footnote_line_container = sorted(footnote_line_container, key=lambda container: container.y0)
        footnote_line = footnote_line_container[0].y0
        footnotes_page = [container for container in text_containers if all([
            container.y0 < footnote_line,
            round(container.x0) < 284,
            get_main_text_size([container]) < main_text_size])]
        text_containers = [container for container in text_containers if container not in footnotes_page]
        return text_containers, footnotes_page
    else:
        return text_containers, None


def get_endnotes_using_separator(page: LTPage, text_containers: List[LTTextContainer],
                                 left_margin: int, main_text_size: int) \
        -> (List[LTTextContainer], Optional[List[LTTextContainer]]):
    if endnote_line_container := [container for container in page if all([
        isinstance(container, LTRect),
        container.height < 1,
        container.width < 150,
        round(container.x0) == left_margin
    ])]:
        endnote_line_container = sorted(endnote_line_container, key=lambda container: container.y0)
        endnote_line = endnote_line_container[0].y0
        endnotes = [container for container in text_containers if all([
            container.y0 < endnote_line,
            get_main_text_size([container]) < main_text_size])]
        text_containers = [container for container in text_containers if container not in endnotes]
        return text_containers, endnotes
    else:
        return text_containers, None


def construct_footnotes(footnotes: List[LTTextContainer]) -> Dict[str, str]:
    footnote_text = []
    result = []
    for container in footnotes:
        footnote_string = container.get_text().strip()
        footnote_text.append(footnote_string)
        if re.search(r'[.?!"”]\s*$', footnote_string):
            if footnote_mark := re.match(r'\d+\s+', footnote_text[0].strip()):
                footnote_mark = footnote_mark.group(0).strip()
                footnote = ' '.join(footnote_text).replace(footnote_mark, '', 1).strip()
                result.append((footnote_mark, footnote))
                logger.info(f"Found a footnote: ({footnote_mark}, {footnote})")
            else:
                logger.warning(f'No footnote mark found: {footnote_text[0].strip()}')
                if len(result) > 0:
                    logger.info(f'Appending to previous footnote.')
                    footnote_text.insert(0, result[-1][1])
                    footnote = ' '.join(footnote_text).strip()
                    result[-1] = (result[-1][0], footnote)
                else:
                    logger.error(f"Nowhere to put footnote. Abandoning: {' '.join(footnote_text)}")
            footnote_text.clear()
    return dict(result)


class BaseCorpusDocumentFactory:
    """Base class for a factory to produce CorpusDocuments. Provides a basic extraction of text containers from PDF."""

    def __init__(self, **kwargs):
        self.data: Dict[str, any] = dict(kwargs)
        self._result = CorpusDocument(source=self.data.get('source', None))
        self._text_containers: List[List[LTTextContainer]] = []
        self._pages: List[LTPage] = []

    def pre_process(self):
        """Actions to do be fore each paragraph is processed. Use this to initialize metadata
        or clean text containers."""
        if pdf := self.data.get('pdf', None):
            with open(pdf, 'rb') as pdf:
                self._extract_pages_and_text_containers(pdf)
        elif source := self.data.get('source', None):
            with PDFFile(source, self.data.get('options', None)) as file:
                self._extract_pages_and_text_containers(file)

    def process_all(self):
        """Process all pages. This is the entry point to processing pages and paragraphs."""
        for index, page_containers in enumerate(self._text_containers):
            self.process_page(page_containers)

    def process_page(self, page_containers: List[LTTextContainer]):
        """Process a page. This is the entry point to processing a page and its paragraphs."""
        for index, container in enumerate(page_containers):
            self.process_paragraph(container, index, page_containers)

    def process_paragraph(self, paragraph: LTTextContainer, index: int, page_containers: List[LTTextContainer]):
        """Process a paragraph. The default add a paragraph to the CorpusDocument"""
        self._result.add_paragraph(paragraph.get_text().strip(), str(index))

    def get_result(self) -> CorpusDocument:
        """Convenience method to call all processing methods and return the result CorpusDocument."""
        self.pre_process()
        self.process_all()
        return self._result

    def _extract_pages_and_text_containers(self, pdf):
        """Method called to prepare the pages and containers from pdf for processing during pre-process."""
        self._pages = list(extract_pages(pdf, laparams=self.data.get('laparams', None)))
        for page in self._pages:
            self._text_containers.append([element for element in page if
                                          isinstance(element, LTTextContainer) and
                                          element.get_text() != '' and not
                                          re.search(r'^\s+$', element.get_text())])

    def get_text_containers(self, page_numbers: Optional[List[int]] = None, filter_function=lambda container: True,
                            custom_container: List[List[LTTextContainer]] = None) \
            -> Generator[LTTextContainer, None, None]:
        """
        Convenience method to generate a list of containers from the source/PDF.

        :param page_numbers: Array of zero-indexed pages to extract. Default is to extract from all pages.
        :param filter_function: Function to call to filter extracted text containers.
            Function accepts one parameter being the container to retain or reject.
            Function should return a boolean (True if the container should be retained)
        :param custom_container: The containers which should be processed.
            Default is the main text containers in the factory.
        :return:
        """
        if custom_container is None:
            custom_container = self._text_containers
        if not page_numbers:
            for page in custom_container:
                for container in page:
                    if filter_function(container):
                        yield container
        else:
            for index in page_numbers:
                for page in custom_container[index]:
                    for container in page:
                        if filter_function(container):
                            yield container

    @classmethod
    def from_pdf(cls, pdf, **kwargs) -> CorpusDocument:
        """Class method to create a CorpusDocument from a PDF."""
        factory = cls(pdf=pdf, **kwargs)
        return factory.get_result()

    @classmethod
    def from_decision_item(cls, source: PDPCDecisionItem, options: Options = None, **kwargs) -> CorpusDocument:
        """Class method to create a CorpusDocument from a PDPCDecisionItem."""
        factory = cls(source=source, options=options, **kwargs)
        return factory.get_result()

    @classmethod
    def check_decision(cls, item: Optional[PDPCDecisionItem] = None, options: Optional[Options] = None) -> bool:
        """Class method to check if the Item should be handled by this Factory.
        Returns false for BaseCorpusDocumentFactory."""
        return False
