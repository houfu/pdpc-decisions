#  MIT License Copyright (c) 2020. Houfu Ang

import requests

from pdpc_decisions.scraper import get_url, get_respondent, get_published_date, get_summary, get_title, \
    PDPCDecisionItem, Scraper


def test_site_url():
    r = requests.get('https://www.pdpc.gov.sg/Commissions-Decisions/Data-Protection-Enforcement-Cases')
    assert r.status_code == 200, "Error getting PDPC Enforcement website"


def test_site_url_structure(selenium):
    selenium.get('https://www.pdpc.gov.sg/Commissions-Decisions/Data-Protection-Enforcement-Cases')
    decisions = selenium.find_elements_by_class_name('press-item')
    assert len(decisions) == 5, "Visited PDPC website, but could not match number of decisions on site. " \
                                "Has the site changed its layout or structure?"


def test_item_dates(decisions_test_items, decisions_gold):
    for idx, item in enumerate(decisions_test_items):
        result = get_published_date(item)
        assert result == decisions_gold[idx].published_date


def test_item_respondent(decisions_test_items, decisions_gold):
    for idx, item in enumerate(decisions_test_items):
        result = get_respondent(item)
        assert result == decisions_gold[idx].respondent


def test_item_summary(decisions_test_items, decisions_gold):
    for idx, item in enumerate(decisions_test_items):
        result = get_summary(item)
        assert result == decisions_gold[idx].summary


def test_item_title(decisions_test_items, decisions_gold):
    for idx, item in enumerate(decisions_test_items):
        result = get_title(item)
        assert result == decisions_gold[idx].title


def test_item_download_url(decisions_test_items, decisions_gold):
    for idx, item in enumerate(decisions_test_items):
        result = get_url(item)
        assert result == decisions_gold[idx].download_url


def test_item_conversion(decisions_test_items, decisions_gold):
    for idx, item in enumerate(decisions_test_items):
        result = PDPCDecisionItem(item)
        assert result.published_date == decisions_gold[idx].published_date
        assert result.download_url == decisions_gold[idx].download_url
        assert result.respondent == decisions_gold[idx].respondent
        assert result.summary == decisions_gold[idx].summary
        assert result.title == decisions_gold[idx].title


def test_scraper_init():
    scraper = Scraper()
    assert scraper


def test_scraper_scrape(decisions_gold, get_test_page_url):
    scraper = Scraper()
    result = scraper.scrape(
        site_url=get_test_page_url)
    assert len(result) == len(decisions_gold) * 26
