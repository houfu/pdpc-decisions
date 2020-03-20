#  MIT License Copyright (c) 2020. Houfu Ang
import pdpc_decisions.scraper_extras as extras


def test_get_enforcement(decisions_gold):
    extras.get_enforcement(decisions_gold)
    assert decisions_gold[0].enforcement == ['directions']
    assert decisions_gold[1].enforcement == [['financial', 54000]]
    assert decisions_gold[2].enforcement == [['financial', 16000]]
    assert decisions_gold[3].enforcement == [['financial', 5000]]
    assert decisions_gold[4].enforcement == [['financial', 24000], ['financial', 12000]]


def test_get_decision_citation(decisions_extras_gold):
    extras.get_decision_citation_all(decisions_extras_gold)
    assert decisions_extras_gold[0].citation == '[2020] SGPDPC 1'
    assert decisions_extras_gold[0].case_number == 'DP-1234-5678A'


def test_get_case_references(requests_mock):
    import pickle
    import os
    decisions = pickle.load(open(os.path.join(os.getcwd(), 'tests', 'decisions_references.pickle'), 'rb'))
    with open('tests/test_reference_1.pdf', 'rb') as html:
        content = html.read()
    requests_mock.get('mock://get_test_pdf_url_1.pdf', content=content)
    with open('tests/test_reference_2.pdf', 'rb') as html:
        content = html.read()
    requests_mock.get('mock://get_test_pdf_url_2.pdf', content=content)
    with open('tests/test_reference_3.pdf', 'rb') as html:
        content = html.read()
    requests_mock.get('mock://get_test_pdf_url_3.pdf', content=content)
    with open('tests/test.pdf', 'rb') as html:
        bytes = html.read()
    requests_mock.get('mock://get_test_pdf_url.pdf', content=bytes)

    extras.get_case_references(decisions)
    assert decisions[0].referring_to == ['[2020] SGPDPC 3', '[2019] SGPDPC 1', '[2016] SGPDPC 5']
    assert decisions[0].referred_by == []
    assert decisions[1].referring_to == []
    assert decisions[1].referred_by == ['[2020] SGPDPC 1']
    assert decisions[2].referring_to == []
    assert decisions[2].referred_by == []


def test_scraper_extras(decisions_gold):
    assert extras.scraper_extras(decisions_gold)
