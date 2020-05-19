#  MIT License Copyright (c) 2020. Houfu Ang
import logging
from typing import List

from pdpc_decisions.download_file import check_pdf
from .scraper import PDPCDecisionItem


def get_enforcement(items: List[PDPCDecisionItem]) -> None:
    """
    Get enforcement details for a list of PDPCDecisionItem.
    The results are saved as the field `enforcement` in the item in the following format.
    (**Type of enforcement**, **the penalty sum for financial penalties**)
    :param items: A list of PDPCDecisionItems to be assessed.
    :return: None
    """
    import spacy
    from spacy.matcher import Matcher
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)
    financial_penalty_pattern = [{'LOWER': 'financial'},
                                 {'LOWER': 'penalty'},
                                 {'POS': 'ADP'},
                                 {'LOWER': '$'},
                                 {'LIKE_NUM': True}]
    financial_1_id = 'financial_1'
    matcher.add(financial_1_id, [financial_penalty_pattern])
    financial_penalty_pattern2 = [{'LOWER': 'financial'},
                                  {'LOWER': 'penalty'},
                                  {'POS': 'ADP'},
                                  {'LOWER': '$'},
                                  {'LIKE_NUM': True},
                                  {'LOWER': 'and'},
                                  {'LOWER': '$'},
                                  {'LIKE_NUM': True}]
    financial_2_id = 'financial_2'
    matcher.add(financial_2_id, [financial_penalty_pattern2])
    warning_pattern = [{'LOWER': 'warning'},
                       {'POS': 'AUX'},
                       {'LOWER': 'issued'}]
    warning_id = 'warning'
    matcher.add(warning_id, [warning_pattern])
    directions_pattern = [{'LOWER': 'directions'},
                          {'POS': 'AUX'},
                          {'LOWER': 'issued'}]
    directions_id = 'directions'
    matcher.add(directions_id, [directions_pattern])
    logging.info('Adding enforcement information to items.')
    for item in items:
        doc = nlp(item.summary)
        matches = matcher(doc)
        item.enforcement = []
        for match in matches:
            match_id, _, end = match
            if nlp.vocab.strings[financial_2_id] in match:
                span1 = doc[end - 4: end - 3]
                value = ['financial', int(span1.text.replace(',', ''))]
                if not item.enforcement.count(value):
                    item.enforcement.append(value)
                span2 = doc[end - 1:end]
                value = ['financial', int(span2.text.replace(',', ''))]
                if not item.enforcement.count(value):
                    item.enforcement.append(value)
            if nlp.vocab.strings[financial_1_id] in match:
                span = doc[end - 1:end]
                value = ['financial', int(span.text.replace(',', ''))]
                if not item.enforcement.count(value):
                    item.enforcement.append(value)
            if nlp.vocab.strings[warning_id] in match:
                item.enforcement.append(warning_id)
            if nlp.vocab.strings[directions_id] in match:
                item.enforcement.append(directions_id)


def get_decision_citation_all(items: List[PDPCDecisionItem]) -> None:
    """
    Gets the citation and case number for a list of PDPCDecisionItem.
    The result is saved in fields "citation" and "case_number" respectively.
    :param items:
    :return: None
    """
    logging.info('Adding citation information to items.')
    for item in items:
        item.citation, item.case_number = get_decision_citation_item(item)


def get_decision_citation_item(source: PDPCDecisionItem) -> (str, str):
    """
    Gets the citation and case number for a PDPCDecisionItem.
    :param source: The PDPCDecisionItem to get the citation and case number.
    :return: A tuple consisting of (citation, case_number)
    """
    from pdfminer.high_level import extract_text_to_fp
    import requests
    import io
    import re
    r = requests.get(source.download_url)
    citation = ''
    case_number = ''
    if check_pdf(source.download_url):
        with io.BytesIO(r.content) as pdf, io.StringIO() as output_string:
            extract_text_to_fp(pdf, output_string, page_numbers=[0, 1])
            contents = output_string.getvalue()
        summary_match = re.search(r'SUMMARY OF THE DECISION', contents)
        if not summary_match:
            citation_match = re.search(r'(\[\d{4}])\s+((?:\d\s+)?[A-Z|()]+)\s+\[?(\d+)\]?', contents)
            if citation_match:
                citation = citation_match.expand(r'\1 \2 \3')
        case_match = re.search(r'DP-\w*-\w*', contents)
        if case_match:
            case_number = case_match.group()
    return citation, case_number


def get_case_references_all(items: List[PDPCDecisionItem]) -> None:
    """
    Gets the references to cases in each PDPCDecisionItem in items.
    Adds the PDPCDecisionItem to a list of references in a target PDPCDecisionItem.
    The actions are saved in a parameter "referring_to" and "referred_by" of a PDPCDecisionItem respectively.
    :param items:
    :return:
    """
    logging.info('Adding case reference information to items.')
    # construct referring to index
    for item in items:
        citation, _ = get_decision_citation_item(source=item)
        item.referring_to = get_referring_to_item(item, citation=citation)
        add_referred_by_to_item(source=item, target=items, citation=citation)


def add_referred_by_to_item(source: PDPCDecisionItem, target: List[PDPCDecisionItem], citation: str) -> None:
    """
    Adds the source PDPCDecisionItem to a PDPCDecisionItem's "referred_by" field in target
    if source makes a reference to an item in target. The method finds references by citation.
    :param citation: Citation of source.
    :param source:
    :param target:
    :return:
    """
    if not hasattr(source, 'referring_to'):
        return
    for reference in source.referring_to:
        result_item = next((x for x in target if x.citation == reference), None)
        if result_item:
            if not hasattr(result_item, 'referred_by'):
                result_item.referred_by = [citation]
            if result_item.referred_by.count(citation) == 0:
                result_item.referred_by.append(citation)


def get_referring_to_item(source: PDPCDecisionItem, citation: str) -> List[str]:
    """
    Gets the references to cases made in source PDPCDecisionItem.
    :param citation: Citation of source
    :param source:
    :return: A list of case references/citations.
    """
    referring_to = []
    if check_pdf(source.download_url):
        from .download_file import get_text_from_pdf
        contents = get_text_from_pdf(source)
        import re
        citation_regex = re.compile(r'(\[\d{4}])\s+((?:\d\s+)?[A-Z|()]+)\s+\[?(\d+)\]?')
        citation_matches = citation_regex.finditer(contents)
        for match in citation_matches:
            result_citation = match.expand(r'\1 \2 \3')
            if (referring_to.count(result_citation) == 0) and (result_citation != citation):
                referring_to.append(result_citation)
    return referring_to


def scraper_extras(items):
    logging.info('Start adding extra information to items.')
    get_decision_citation_all(items)
    get_enforcement(items)
    get_case_references_all(items)
    logging.info('End adding extra information to items.')
    return True
