#  MIT License Copyright (c) 2020. Houfu Ang

import datetime
import os
from pathlib import Path

import pytest

import pdpc_decisions.scraper as scraper


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(25)
    return selenium


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--no-sandbox')
    return chrome_options


@pytest.fixture()
def decisions_test_items():
    test_items_url = [
        Path(os.getcwd() + '/tests/test_items/test_1.html').as_uri(),
        Path(os.getcwd() + '/tests/test_items/test_2.html').as_uri(),
        Path(os.getcwd() + '/tests/test_items/test_3.html').as_uri(),
        Path(os.getcwd() + '/tests/test_items/test_4.html').as_uri(),
        Path(os.getcwd() + '/tests/test_items/test_5.html').as_uri(),
    ]
    test_decision_gold_dict = [
        {'published_date': datetime.date(2016, 4, 21), 'respondent': 'Institution of Engineers, Singapore',
         'title': 'Breach of Protection Obligation by Institution of Engineers, Singapore',
         'summary': 'A financial penalty of $10,000 was imposed and directions issued to the Institution of '
                    'Engineers, Singapore for failing to implement proper and adequate protective measures to secure '
                    'its IT system, resulting in unauthorised disclosure of the personal data of more than 4,'
                    '000 members.',
         'download_url': 'file:///-/media/Files/PDPC/PDF-Files/Commissions-Decisions/grounds-of-decision---institute'
                         '-of-engineers-singapore-(210416).pdf?la=en'},
        {'published_date': datetime.date(2020, 3, 19),
         'respondent': 'MCST 4375 and Breach of the Protection Obligation',
         'title': 'Breach of the Protection and Accountability Obligations by MCST 4375 and Breach of the Protection '
                  'Obligation by A Best Security Management',
         'summary': 'Both MCST 4375 and A Best Security Management failed to put in place reasonable security '
                    'arrangements to prevent the unauthorised disclosure of CCTV footage of an individual injured by '
                    'a falling glass door at Alexandra Central Mall. MCST 4375 also failed to put in place policies '
                    'and practices necessary for the organisation to comply with the PDPA.',
         'download_url': 'file:///-/media/Files/PDPC/PDF-Files/Commissions-Decisions/MCST-4375-and-Others---Decision'
                         '---03022020.pdf'},
        {'published_date': datetime.date(2019, 12, 5), 'respondent': 'Honestbee',
         'title': 'Breach of the Protection Obligation by Honestbee',
         'summary': 'A financial penalty of $8,000 was imposed on Honestbee for failing to put in place reasonable '
                    'security arrangements to protect the personal data of individuals. The data of about 8,'
                    '000 individuals was stored in the cloud without access restrictions.',
         'download_url': 'file:///-/media/Files/PDPC/PDF-Files/Commissions-Decisions/Summary-Decision---Honestbee.pdf'
                         '?la=en'},
        {'published_date': datetime.date(2020, 1, 9), 'respondent': 'Globalsign.in Pte Ltd',
         'title': 'Breach of the Protection and Retention Obligations by Globalsign.in Pte Ltd',
         'summary': 'A financial penalty of $34,000 was imposed on Globalsign.in for failing to put in place '
                    'reasonable security arrangements to protect the personal data supplied by its clients. '
                    'Globalsign.in, which sends mass marketing emails on behalf of its clients to their respective '
                    'customers, was also found to be holding personal data which was no longer necessary for legal or '
                    'business purposes.',
         'download_url': 'file:///-/media/Files/PDPC/PDF-Files/Commissions-Decisions/Decision--MSIG-Insurance'
                         '-Singapore-Pte-Ltd--191119.pdf?la=en'},
        {'published_date': datetime.date(2020, 2, 11), 'respondent': 'SPH Magazines',
         'title': 'Breach of the Protection Obligation by SPH Magazines',
         'summary': 'A financial penalty of $26,000 was imposed on SPH Magazines for failing to put in place '
                    'reasonable security arrangements to prevent the unauthorised access of personal data of members '
                    'of HardwareZone forum site.',
         'download_url': 'file:///-/media/Files/PDPC/PDF-Files/Commissions-Decisions/Decision---SPH-Magazines-Pte-Ltd'
                         '.pdf'}
    ]
    test_decision_gold = [scraper.PDPCDecisionItem(**dictionary) for dictionary in test_decision_gold_dict]
    return test_items_url, test_decision_gold


@pytest.fixture()
def decisions_gold(requests_mock):
    import datetime
    with open('tests/test.pdf', 'rb') as html:
        bytes = html.read()
    requests_mock.get('mock://test/get_test_pdf_url.pdf', content=bytes)
    with open('tests/test_text_page.htm', 'r') as html:
        text = html.read()
    requests_mock.get('mock://test/get_test_txt_path', text=text)
    return [
        scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2), respondent='Avant Logistic Service',
                                 download_url='mock://test/get_test_pdf_url.pdf',
                                 title='Breach of the Protection Obligation by Avant Logistic Service',
                                 summary="Breach of the Protection Obligation by Avant Logistic Service. "
                                         "Directions were issued to Avant Logistic Service for failing to "
                                         "make reasonable security arrangements to prevent the unauthorised "
                                         "disclosure of customers' personal data. The lapses resulted in "
                                         "personal data of customers being disclosed by an employee."),
        scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2), respondent='Horizon Fast Ferry',
                                 download_url='mock://test/get_test_txt_path',
                                 title='Breach of the Protection Obligation by Horizon Fast Ferry',
                                 summary="Breach of the Protection Obligation by Horizon Fast Ferry. "
                                         "A financial penalty of $54,000 was imposed on Horizon Fast Ferry for "
                                         "failing to appoint a data protection officer, develop and implement "
                                         "data protection policies and practices, and put in place reasonable "
                                         "security arrangements to protect the personal data collected "
                                         "from its customers."),
        scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2), respondent='Genki Sushi',
                                 download_url='mock://test/get_test_pdf_url.pdf',
                                 title='Breach of the Protection Obligation by Genki Sushi',
                                 summary="Breach of the Protection Obligation by Genki Sushi. "
                                         "A financial penalty of $16,000 was imposed on Genki Sushi for failing "
                                         "to put in place reasonable security arrangements to protect personal data "
                                         "of its employees. The incident resulted in the data being subjected to "
                                         "a ransomware attack."),
        scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2), respondent='Championtutor',
                                 download_url='mock://test/get_test_pdf_url.pdf',
                                 title='Breach of the Openness Obligation by Championtutor',
                                 summary="Breach of the Openness Obligation by Championtutor. "
                                         "Directions, including a financial penalty of $5,000, were imposed on "
                                         "Championtutor for breaches of the PDPA. The organisation failed to "
                                         "appoint a data protection officer and did not have written policies and "
                                         "practices necessary to ensure its compliance with  the PDPA."),
        scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2),
                                 respondent='CDP and Toppan Security Printing',
                                 download_url='mock://test/get_test_pdf_url.pdf',
                                 title='Breach of the Protection Obligation by CDP and Toppan Security Printing',
                                 summary="Breach of the Protection Obligation by CDP and Toppan Security Printing. "
                                         "A financial penalty of $24,000 and $12,000 was imposed on CDP and "
                                         "Toppan Security Printing respectively for failing to put in place "
                                         "reasonable security arrangements to protect the data of CDP’s account "
                                         "holders from unauthorised disclosure. The incident resulted in other "
                                         "account holders’ data being printed on another account holder’s "
                                         "notification letter. An application for reconsideration was made by "
                                         "Toppan Security Printing. Upon reconsideration, "
                                         "directions in the decision were varied. ")
    ]


@pytest.fixture()
def decisions_extras_gold(requests_mock):
    import pdpc_decisions.scraper as scraper
    import datetime
    with open('tests/test_reference_1.pdf', 'rb') as html:
        content = html.read()
    requests_mock.get('mock://test/get_test_pdf_url_1.pdf', content=content)
    with open('tests/test_reference_2.pdf', 'rb') as html:
        content = html.read()
    requests_mock.get('mock://test/get_test_pdf_url_2.pdf', content=content)
    with open('tests/test_reference_3.pdf', 'rb') as html:
        content = html.read()
    requests_mock.get('mock://test/get_test_pdf_url_3.pdf', content=content)
    with open('tests/test.pdf', 'rb') as html:
        bytes = html.read()
    requests_mock.get('mock://test/get_test_pdf_url.pdf', content=bytes)
    result = []
    # 0
    item = scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2), respondent='Avant Logistic Service',
                                    download_url='mock://test/get_test_pdf_url_1.pdf',
                                    title='Breach of the Protection Obligation by Avant Logistic Service',
                                    summary="Breach of the Protection Obligation by Avant Logistic Service. "
                                            "Directions were issued to Avant Logistic Service for failing to "
                                            "make reasonable security arrangements to prevent the unauthorised "
                                            "disclosure of customers' personal data. The lapses resulted in "
                                            "personal data of customers being disclosed by an employee.")
    item.case_number = 'DP-1234-5678A'
    item.citation = '[2020] SGPDPC 1'
    item.enforcement = ['directions']
    item.referred_by = []
    item.referring_to = ['[2020] SGPDPC 3', '[2019] SGPDPC 1', '[2016] SGPDPC 5']
    result.append(item)
    # 1
    item = scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2), respondent='Horizon Fast Ferry',
                                    download_url='mock://test/get_test_pdf_url_2.pdf',
                                    title='Breach of the Protection Obligation by Horizon Fast Ferry',
                                    summary="Breach of the Protection Obligation by Horizon Fast Ferry. "
                                            "A financial penalty of $54,000 was imposed on Horizon Fast Ferry for "
                                            "failing to appoint a data protection officer, develop and implement "
                                            "data protection policies and practices, and put in place reasonable "
                                            "security arrangements to protect the personal data collected "
                                            "from its customers.")
    item.case_number = 'DP-1234-5678A'
    item.citation = '[2020] SGPDPC 3'
    item.enforcement = ['financial', 54000]
    item.referred_by = ['[2020] SGPDPC 1']
    item.referring_to = []
    result.append(item)
    # 2
    item = scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2), respondent='Genki Sushi',
                                    download_url='mock://test/get_test_pdf_url_3.pdf',
                                    title='Breach of the Protection Obligation by Genki Sushi',
                                    summary="Breach of the Protection Obligation by Genki Sushi. "
                                            "A financial penalty of $16,000 was imposed on Genki Sushi for failing "
                                            "to put in place reasonable security arrangements to protect personal data "
                                            "of its employees. The incident resulted in the data being subjected to "
                                            "a ransomware attack.")
    item.case_number = 'DP-1234-5678A'
    item.citation = '[2018] SGPDPC 3'
    item.enforcement = [['financial', 16000]]
    item.referred_by = []
    item.referring_to = []
    result.append(item)
    # 3
    item = scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2), respondent='Championtutor',
                                    download_url='mock://test/get_test_pdf_url.pdf',
                                    title='Breach of the Openness Obligation by Championtutor',
                                    summary="Breach of the Openness Obligation by Championtutor. "
                                            "Directions, including a financial penalty of $5,000, were imposed on "
                                            "Championtutor for breaches of the PDPA. The organisation failed to "
                                            "appoint a data protection officer and did not have written policies and "
                                            "practices necessary to ensure its compliance with  the PDPA.")
    item.case_number = 'DP-1811-B3058'
    item.citation = '[2020] SGPDPC 1'
    item.enforcement = [['financial', 5000]]
    item.referred_by = []
    item.referring_to = []
    result.append(item)
    # 4
    item = scraper.PDPCDecisionItem(published_date=datetime.date(2019, 8, 2),
                                    respondent='CDP and Toppan Security Printing',
                                    download_url='mock://test/get_test_pdf_url.pdf',
                                    title='Breach of the Protection Obligation by CDP and Toppan Security Printing',
                                    summary="Breach of the Protection Obligation by CDP and Toppan Security Printing. "
                                            "A financial penalty of $24,000 and $12,000 was imposed on CDP and "
                                            "Toppan Security Printing respectively for failing to put in place "
                                            "reasonable security arrangements to protect the data of CDP’s account "
                                            "holders from unauthorised disclosure. The incident resulted in other "
                                            "account holders’ data being printed on another account holder’s "
                                            "notification letter. An application for reconsideration was made by "
                                            "Toppan Security Printing. Upon reconsideration, "
                                            "directions in the decision were varied. ")
    item.case_number = 'DP-1811-B3058'
    item.citation = '[2020] SGPDPC 1'
    item.enforcement = [['financial', 24000], ['financial', 12000]]
    item.referred_by = []
    item.referring_to = []
    result.append(item)
    return result


@pytest.fixture(scope='module')
def options_test():
    return {
        'csv_path': 'tests/temp.csv',
        'download_folder': 'tests/downloads/',
        "corpus_folder": 'tests/corpus/',
        'extras': True
    }


@pytest.fixture(scope='module')
def get_test_page_url():
    return Path(os.getcwd() + '/tests/test_page.html').as_uri()


@pytest.fixture(scope='module')
def get_test_pdf_path():
    return Path(os.getcwd(), 'tests', 'test.pdf')


@pytest.fixture()
def get_test_pdf_url(requests_mock):
    with open('tests/test.pdf', 'rb') as html:
        bytes = html.read()
    requests_mock.get('mock://test/get_test_pdf_url.pdf', content=bytes)
    return 'mock://test/get_test_pdf_url.pdf'


@pytest.fixture()
def get_test_txt_path(requests_mock):
    with open('tests/test_text_page.htm', 'r') as html:
        text = html.read()
    requests_mock.get('mock://test/get_test_txt_path', text=text)
    return 'mock://test/get_test_txt_path'
