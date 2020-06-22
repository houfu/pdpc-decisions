#  MIT License Copyright (c) 2020. Houfu Ang
import pytest
import requests

from pdpc_decisions.classes import PDPCDecisionItem


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


def test_item_conversion(decisions_test_items):
    test, gold = decisions_test_items
    for idx, url in enumerate(test):
        result = PDPCDecisionItem.from_web_page(url)
        assert result.published_date == gold[idx].published_date
        assert result.download_url[12:] == gold[idx].download_url[12:]
        assert result.respondent == gold[idx].respondent
        assert result.summary == gold[idx].summary
        assert result.title == gold[idx].title


def test_scraper_init():
    from pdpc_decisions.scraper import Scraper
    assert Scraper()


@pytest.mark.skip('Change in site structure rendered this inapplicable')
def test_scraper_scrape(get_test_page_url, mocker):
    pass

