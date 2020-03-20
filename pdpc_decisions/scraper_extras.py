#  MIT License Copyright (c) 2020. Houfu Ang


def get_enforcement(items):
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

    for item in items:
        doc = nlp(item.summary)
        matches = matcher(doc)
        result = []
        for match in matches:
            match_id, _, end = match
            if nlp.vocab.strings[financial_2_id] in match:
                span1 = doc[end - 4: end - 3]
                value = ['financial', int(span1.text.replace(',', ''))]
                if not result.count(value):
                    result.append(value)
                span2 = doc[end - 1:end]
                value = ['financial', int(span2.text.replace(',', ''))]
                if not result.count(value):
                    result.append(value)
            if nlp.vocab.strings[financial_1_id] in match:
                span = doc[end - 1:end]
                value = ['financial', int(span.text.replace(',', ''))]
                if not result.count(value):
                    result.append(value)
            if nlp.vocab.strings[warning_id] in match:
                result.append(warning_id)
            if nlp.vocab.strings[directions_id] in match:
                result.append(directions_id)
        if result:
            item.enforcement = result


def get_decision_citation_all(items):
    for item in items:
        get_decision_citation_one(item)


def get_decision_citation_one(item):
    from pdfminer.high_level import extract_text_to_fp
    import requests
    import io
    import re
    r = requests.get(item.download_url)
    item.citation = ''
    item.case_number = ''
    if item.download_url[-3:] == 'pdf':
        with io.BytesIO(r.content) as pdf, io.StringIO() as output_string:
            extract_text_to_fp(pdf, output_string, page_numbers=[0, 1])
            contents = output_string.getvalue()
        match = re.search(r'\[\d{4}]\s+(?:\d\s+)?[A-Z|()]+\s+\d+', contents)
        if match:
            item.citation = match.group()
        match = re.search(r'DP-\w*-\w*', contents)
        if match:
            item.case_number = match.group()


def get_case_references(items):
    import spacy
    from spacy.matcher import Matcher
    from .download_file import get_text_from_pdf
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)
    citation_pattern = [{"IS_BRACKET": True},
                        {"SHAPE": "dddd"},
                        {"IS_BRACKET": True},
                        {"LIKE_NUM": True, "OP": "?"},
                        {"TEXT": {"REGEX": "^[A-Z]"}, "OP": "?"},
                        {"ORTH": ".", "OP": "?"},
                        {"TEXT": {"REGEX": r"^[A-Z\.]"}},
                        {"ORTH": ".", "OP": "?"},
                        {"LIKE_NUM": True}]
    matcher.add('citations', [citation_pattern])
    # construct referring to index
    for item in items:
        if not hasattr(item, 'citation'):
            get_decision_citation_one(item)
        item.referred_by = []
        item.referring_to = []
        if item.download_url[-3:] == 'pdf':
            doc = nlp(get_text_from_pdf(item))
            matches = matcher(doc)
            for match in matches:
                _, start, end = match
                result_citation = doc[start:end].text
                if not result_citation == item.citation:
                    if not hasattr(item, 'referring_to'):
                        item.referring_to = [result_citation]
                    else:
                        item.referring_to.append(result_citation)
    # constructed referred by index
    for item in items:
        for reference in item.referring_to:
            result_item = next((x for x in items if x.citation == reference), None)
            if result_item:
                if result_item.referred_by.count(item.citation) == 0:
                    result_item.referred_by.append(item.citation)
                else:
                    result_item.referred_by = [item.citation]


def scraper_extras(items):
    get_decision_citation_all(items)
    get_enforcement(items)
    get_case_references(items)
    return True
