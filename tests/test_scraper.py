#  MIT License Copyright (c) 2020. Houfu Ang
import pytest
import requests

import pdpc_decisions.scraper as scraper


def test_site_url():
    r = requests.get('https://www.pdpc.gov.sg/All-Commissions-Decisions?'
                     'keyword=&industry=all&nature=all&decision=all&penalty=all&page=1')
    assert r.status_code == 200, "Error getting PDPC Enforcement website"


def test_site_url_structure(selenium):
    selenium.get('https://www.pdpc.gov.sg/All-Commissions-Decisions?'
                 'keyword=&industry=all&nature=all&decision=all&penalty=all&page=1')
    decisions = selenium.find_element_by_class_name('listing__list').find_elements_by_tag_name('li')
    assert len(decisions) == 8, "Visited PDPC website, but could not match number of decisions on site. " \
                                "Has the site changed its layout or structure?"


def test_item_dates(decisions_test_items, selenium):
    test, gold = decisions_test_items
    for idx, url in enumerate(test):
        selenium.get(url)
        item = selenium.find_element_by_class_name('detail-content')
        result = scraper.get_published_date(item)
        assert result == gold[idx].published_date


def test_item_respondent(decisions_test_items, selenium):
    test, gold = decisions_test_items
    for idx, url in enumerate(test):
        selenium.get(url)
        item = selenium.find_element_by_class_name('detail-content')
        result = scraper.get_respondent(item)
        assert result == gold[idx].respondent


def test_item_summary(decisions_test_items, selenium):
    test, gold = decisions_test_items
    for idx, url in enumerate(test):
        selenium.get(url)
        item = selenium.find_element_by_class_name('detail-content')
        result = scraper.get_summary(item)
        assert result == gold[idx].summary


def test_item_title(decisions_test_items, selenium):
    test, gold = decisions_test_items
    for idx, url in enumerate(test):
        selenium.get(url)
        item = selenium.find_element_by_class_name('detail-content')
        result = scraper.get_title(item)
        assert result == gold[idx].title


def test_item_download_url(decisions_test_items, selenium):
    test, gold = decisions_test_items
    for idx, url in enumerate(test):
        selenium.get(url)
        item = selenium.find_element_by_class_name('detail-content')
        result = scraper.get_url(item)
        assert result == gold[idx].download_url


def test_item_conversion(decisions_test_items, selenium):
    test, gold = decisions_test_items
    for idx, url in enumerate(test):
        selenium.get(url)
        item = selenium.find_element_by_class_name('detail-content')
        result = scraper.PDPCDecisionItem.from_element(item)
        assert result.published_date == gold[idx].published_date
        assert result.download_url == gold[idx].download_url
        assert result.respondent == gold[idx].respondent
        assert result.summary == gold[idx].summary
        assert result.title == gold[idx].title


def test_scraper_init():
    from pdpc_decisions.scraper import Scraper
    assert Scraper()


@pytest.mark.skip('Change in site structure rendered this inapplicable')
def test_scraper_scrape(get_test_page_url, mocker):
    pass


def test_pdpcdecision_item_str(decisions_test_items):
    assert print(decisions_test_items[0]) == "PDPCDecision object: 2016-04-21 Institution of Engineers, Singapore"
