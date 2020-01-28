import requests

from pdpc_decisions.scraper import get_url, get_respondent, get_date, get_summary, get_title, PDPCDecisionItem, Scraper


def test_site_url():
    r = requests.get('https://www.pdpc.gov.sg/Commissions-Decisions/Data-Protection-Enforcement-Cases')
    assert r.status_code == 200, "Error getting PDPC Enforcement website"


def test_site_url_structure(selenium):
    selenium.get('https://www.pdpc.gov.sg/Commissions-Decisions/Data-Protection-Enforcement-Cases')
    decisions = selenium.find_elements_by_class_name('press-item')
    assert len(decisions) == 5, "Visited PDPC website, but could not match number of decisions on site. " \
                                "Has the site changed its layout or structure?"


def test_item_dates(decisions_test_items, decisions_gold):
    for item, idx in decisions_test_items:
        result = get_date(item)
        assert result == decisions_gold[idx]['date']


def test_item_respondent(decisions_test_items, decisions_gold):
    for item, idx in decisions_test_items:
        result = get_respondent(item)
        assert result == decisions_gold[idx]['respondent']


def test_item_summary(decisions_test_items, decisions_gold):
    for item, idx in decisions_test_items:
        result = get_summary(item)
        assert result == decisions_gold[idx]['summary']


def test_item_title(decisions_test_items, decisions_gold):
    for item, idx in decisions_test_items:
        result = get_title(item)
        assert result == decisions_gold[idx]['title']


def test_item_download_url(decisions_test_items, decisions_gold):
    for item, idx in decisions_test_items:
        result = get_url(item)
        assert result[-10:] == decisions_gold[idx]['download_url'][
                               -10:]  # Final ten characters only as url front may chage from site to site


def test_item_conversion(decisions_test_items, decisions_gold):
    for item, idx in decisions_test_items:
        result = PDPCDecisionItem(item)
        assert result == decisions_gold[idx]


def test_scraper_init():
    scraper = Scraper()
    assert scraper


def test_scraper_scrape(decisions_gold):
    import os
    import pathlib
    scraper = Scraper()
    site_url= pathlib.Path(os.getcwd() + '/tests/test_page.html').as_uri()
    print(site_url)
    result = scraper.scrape(site_url=site_url)
    assert len(result) == len(decisions_gold) * 26
