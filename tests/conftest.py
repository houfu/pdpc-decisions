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


@pytest.fixture(scope="module")
def decisions_gold():
    import pickle
    return pickle.load(open(os.path.join(os.getcwd(), 'tests', 'decisions'), 'rb'))


@pytest.fixture(scope='module')
def options_test():
    return {
        'csv_path': 'tests/temp.csv',
        'download_folder': 'tests/downloads/',
        "corpus_folder": 'tests/corpus/',
    }


@pytest.fixture(scope='module')
def get_test_page_url():
    return Path(os.getcwd() + '/tests/test_page.html').as_uri()


@pytest.fixture(scope='module')
def get_test_pdf_path():
    return Path(os.getcwd(), 'tests', 'test.pdf')


@pytest.fixture(scope='module')
def get_test_pdf_url():
    return "https://github.com/houfu/pdpc-decisions/raw/master/tests/test.pdf"


@pytest.fixture(scope='module')
def get_test_txt_path():
    return Path(os.getcwd(), 'tests', 'test_text_page.htm')
