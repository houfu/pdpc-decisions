#  MIT License Copyright (c) 2020. Houfu Ang

import os
from pathlib import Path

import pytest


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--no-sandbox')
    return chrome_options


@pytest.fixture(scope='module')
def decisions_test_items(get_test_page_url):
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')

    selenium_test = Chrome(options=options)
    selenium_test.get(get_test_page_url)
    return selenium_test.find_elements_by_class_name('press-item')


@pytest.fixture()
def decisions_gold(requests_mock):
    with open('tests/test.pdf', 'rb') as html:
        bytes = html.read()
    requests_mock.get('mock://get_test_pdf_url.pdf', content=bytes)
    with open('tests/test_text_page.htm', 'r') as html:
        text = html.read()
    requests_mock.get('mock://get_test_txt_path', text=text)
    import pickle
    return pickle.load(open(os.path.join(os.getcwd(), 'tests', 'decisions.pickle'), 'rb'))


@pytest.fixture()
def decisions_extras_gold(requests_mock):
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
    import pickle
    return pickle.load(open(os.path.join(os.getcwd(), 'tests', 'decisions_extras_gold.pickle'), 'rb'))


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
    requests_mock.get('mock://get_test_pdf_url.pdf', content=bytes)
    return 'mock://get_test_pdf_url.pdf'


@pytest.fixture()
def get_test_txt_path(requests_mock):
    with open('tests/test_text_page.htm', 'r') as html:
        text = html.read()
    requests_mock.get('mock://get_test_txt_path', text=text)
    return 'mock://get_test_txt_path'
