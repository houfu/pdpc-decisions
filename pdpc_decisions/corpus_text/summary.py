import logging
import re
from typing import Optional

from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams

import pdpc_decisions.classes
import pdpc_decisions.corpus_text.common as common
from pdpc_decisions.classes import Options, PDPCDecisionItem
from pdpc_decisions.corpus_text.common import BaseCorpusDocumentFactory

logger = logging.getLogger(__name__)


class SummaryDecisionFactory(BaseCorpusDocumentFactory):
    def __init__(self, **kwargs):
        super().__init__(laparams=LAParams(line_margin=1, char_margin=1.5), **kwargs)
        self._custom_text_containers = []
        self._paragraph_mark_containers = []
        self.text_margins = [72]
        self._paragraph_strings = []
        self._assigned_marks = []
        self._paragraph_mark = ''

    def pre_process(self):
        BaseCorpusDocumentFactory.pre_process(self)
        self.text_margins = common.get_text_margins(list(self.get_text_containers()), len(self._pages))
        for page in range(len(self._pages)):
            page_containers = list(self.get_text_containers([page], filter_function=lambda container: round(
                container.x0) in self.text_margins))
            page_containers = sorted(page_containers, key=lambda item: item.x0)
            page_containers = sorted(page_containers, key=lambda container: container.y0, reverse=True)
            self._custom_text_containers.append(page_containers)
        self._custom_text_containers[0] = self._custom_text_containers[0][1:]

    def process_all(self):
        for index, page_containers in enumerate(self._custom_text_containers):
            self.process_page(page_containers)

    def process_paragraph(self, paragraph, index, page_containers):
        container_string = paragraph.get_text().strip()
        logger.info(f"New container: {container_string}")
        if match := re.match(r'^\d+\.\s*', container_string):
            self._paragraph_mark = match.group(0).strip()
            container_string = container_string.replace(match.group(0), '', 1)
            logger.info(
                f'Matched a paragraph mark: {self._paragraph_mark} and adjusted container string: {container_string}')
        self._paragraph_strings.append(container_string)
        logger.info(f"Add string to paragraph.")
        if re.search(r'[.?!]$', container_string) and (
                len(self._paragraph_strings) == 1 or common.check_gap_before_after_container(page_containers, index)):
            if self._paragraph_mark:
                self._result.add_paragraph(" ".join(self._paragraph_strings), self._paragraph_mark)
                logger.info(f"Added a new paragraph: ({self._paragraph_mark}) {' '.join(self._paragraph_strings)}")
            else:
                logger.info('No paragraph mark found. Appending to previous paragraph.')
                self._paragraph_strings.insert(0, self._result.paragraphs[-1].text)
                self._result.paragraphs[-1].update_text((" ".join(self._paragraph_strings)))
            self._reset()
        logger.info('End of this container')

    def _reset(self):
        self._paragraph_strings.clear()
        self._paragraph_mark = ''
        logger.info('Reset strings and mark')

    @classmethod
    def check_decision(cls, item: Optional[PDPCDecisionItem] = None, options: Optional[Options] = None) -> bool:
        with pdpc_decisions.classes.PDFFile(item, options) as pdf:
            first_page = extract_pages(pdf, page_numbers=[0])
            containers = common.extract_text_containers(first_page)
            for container in containers:
                font, is_only = common.get_common_font_from_paragraph(container)
                if container.get_text().strip() == 'SUMMARY OF THE DECISION' and font == 'TimesNewRomanPS-BoldMT' and is_only:
                    return True
        return False
