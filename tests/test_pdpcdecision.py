#  MIT License Copyright (c) 2020. Houfu Ang
from click.testing import CliRunner

from pdpc_decisions.pdpcdecision import pdpc_decision


def test_pdpc_decision_all(mocker):
    runner = CliRunner()
    scraper = mocker.patch('pdpc_decisions.pdpcdecision.scrape')
    save_file = mocker.patch('pdpc_decisions.pdpcdecision.save_scrape_results_to_csv')
    download_files = mocker.patch('pdpc_decisions.pdpcdecision.download_files')
    create_corpus = mocker.patch('pdpc_decisions.pdpcdecision.create_corpus')
    runner.invoke(pdpc_decision, ['all'])
    scraper.assert_called()
    save_file.assert_called()
    download_files.assert_called()
    create_corpus.assert_called()


def test_pdpc_decision_csv(mocker):
    runner = CliRunner()
    scraper = mocker.patch('pdpc_decisions.pdpcdecision.scrape')
    save_file = mocker.patch('pdpc_decisions.pdpcdecision.save_scrape_results_to_csv')
    runner.invoke(pdpc_decision, ['csv'])
    scraper.assert_called()
    save_file.assert_called()


def test_pdpc_decision_corpus(mocker):
    runner = CliRunner()
    scraper = mocker.patch('pdpc_decisions.pdpcdecision.scrape')
    create_corpus = mocker.patch('pdpc_decisions.pdpcdecision.create_corpus')
    runner.invoke(pdpc_decision, ['corpus'])
    scraper.assert_called()
    create_corpus.assert_called()


def test_pdpc_decision_files(mocker):
    runner = CliRunner()
    scraper = mocker.patch('pdpc_decisions.pdpcdecision.scrape')
    download_files = mocker.patch('pdpc_decisions.pdpcdecision.download_files')
    runner.invoke(pdpc_decision, ['files'])
    scraper.assert_called()
    download_files.assert_called()


def test_pdpc_decision_root_change(mocker):
    import os
    runner = CliRunner()
    mocker.patch('pdpc_decisions.pdpcdecision.scrape')
    mocker.patch('pdpc_decisions.pdpcdecision.download_files')
    original_path = os.getcwd()
    path = os.getcwd() + '/tests'
    runner.invoke(pdpc_decision, ['-r', path, 'files'])
    assert os.getcwd() == path
    os.chdir(original_path)
