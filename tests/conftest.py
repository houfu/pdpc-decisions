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
    yield selenium_test.find_elements_by_class_name('press-item')
    selenium_test.close()


@pytest.fixture(scope="module")
def decisions_gold():
    import pickle
    return pickle.load(open('tests/decisions', 'rb'))


@pytest.fixture(scope='module')
def options_test():
    return {
        'csv_path': 'tests/temp_csv.csv',
        'download_folder': 'tests/download/',
        "corpus_folder": 'tests/download/',
    }


@pytest.fixture(scope='module')
def get_test_page_url():
    import os
    import pathlib
    return pathlib.Path(os.getcwd() + '/tests/test_page.html').as_uri()
