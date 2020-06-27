import os
from unittest.mock import call

from pdfminer.high_level import extract_pages

import pdpc_decisions.corpus_text.common as common
import pdpc_decisions.corpus_text.corpus as corpus
from pdpc_decisions.classes import CorpusDocument


def test_get_main_text_size(get_test_decision_standard_pdf_path):
    pages = extract_pages(get_test_decision_standard_pdf_path.open('rb'), page_numbers=[1])
    text_containers = common.extract_text_containers(pages)
    assert common.get_main_text_size(text_containers) == 12


def test_extract_text_containers(get_test_decision_standard_pdf_path):
    page = extract_pages(get_test_decision_standard_pdf_path.open('rb'), page_numbers=[1])
    text_containers = common.extract_text_containers(page)
    assert len(text_containers) == 31
    page = extract_pages(get_test_decision_standard_pdf_path.open('rb'), page_numbers=[2])
    text_containers = common.extract_text_containers(page)
    assert len(text_containers) == 33


def test_check_first_page_is_cover(get_test_decision_standard_pdf_path, get_test_decision_v1_pdf_path):
    assert common.check_first_page_is_cover(get_test_decision_standard_pdf_path.open('rb'))
    assert not common.check_first_page_is_cover(get_test_decision_v1_pdf_path.open('rb'))


def test_get_common_font_from_pages(get_test_decision_standard_pdf_path, get_test_decision_v1_pdf_path):
    pages_1 = extract_pages(get_test_decision_standard_pdf_path.open('rb'))
    assert common.get_common_font_from_pages(list(pages_1)) == 'TimesNewRomanPSMT'
    pages_2 = extract_pages(get_test_decision_v1_pdf_path.open('rb'))
    assert common.get_common_font_from_pages(list(pages_2)) == 'Arial'


def test_get_document(decisions_corpus_gold, options_test):
    assert corpus.get_document(options_test, decisions_corpus_gold[0])
    options_test.update(extra_corpus=True)
    assert corpus.get_document(options_test, decisions_corpus_gold[1])


def test_create_corpus_file(decisions_corpus_gold, options_test):
    corpus_folder = options_test["corpus_folder"]
    try:
        if not os.path.exists(corpus_folder):
            os.mkdir(corpus_folder)
        destination = corpus.create_corpus_file(options_test, decisions_corpus_gold[0])
        assert os.path.isfile(destination)
        corpus.create_corpus_file(options_test, decisions_corpus_gold[0])
        assert os.path.isfile(os.path.join(corpus_folder, f"2019-08-02 [STANDARD] (1).txt"))
        assert os.path.isfile(os.path.join(corpus_folder, f"2019-08-02 [STANDARD] (2).txt"))
        corpus.create_corpus_file(options_test, decisions_corpus_gold[0])
        corpus.create_corpus_file(options_test, decisions_corpus_gold[0])
        assert os.path.isfile(os.path.join(corpus_folder, f"2019-08-02 [STANDARD] (3).txt"))
    finally:
        import shutil
        shutil.rmtree(corpus_folder)


def test_create_corpus(decisions_corpus_gold, options_test, mocker):
    mkdir_func = mocker.patch.object(os, 'mkdir')
    create_corpus = mocker.patch('pdpc_decisions.corpus_text.corpus.create_corpus_file')
    corpus.create_corpus(options_test, decisions_corpus_gold)
    mkdir_func.assert_called()
    create_corpus.assert_has_calls(
        [call(options_test, decisions_corpus_gold[0]), call(options_test, decisions_corpus_gold[1])],
        call(options_test, decisions_corpus_gold[2]))


def test_pre_process(mocker, get_test_decision_standard_pdf_path, decisions_gold):
    process_func = mocker.patch.object(common.BaseCorpusDocumentFactory, '_extract_pages_and_text_containers')
    factory = common.BaseCorpusDocumentFactory(pdf=get_test_decision_standard_pdf_path)
    factory.pre_process()
    process_func.assert_called()
    process_func.reset_mock()
    factory = common.BaseCorpusDocumentFactory(source=decisions_gold[0])
    factory.pre_process()
    process_func.assert_called()


def test_process_all(mocker):
    process_func = mocker.patch.object(common.BaseCorpusDocumentFactory, 'process_page')
    factory = common.BaseCorpusDocumentFactory()
    factory._text_containers = ['A', 'B', 'C']
    factory.process_all()
    process_func.assert_has_calls(calls=[call('A'), call('B'), call('C')])


def test_process_paragraph(mocker, get_test_decision_standard_pdf_path):
    add_func = mocker.patch.object(CorpusDocument, 'add_paragraph')
    factory = common.BaseCorpusDocumentFactory(pdf=get_test_decision_standard_pdf_path)
    factory.pre_process()
    containers = list(factory.get_text_containers([1]))
    factory.process_paragraph(containers[1], 1, containers)
    add_func.assert_called_with(containers[1].get_text().strip(), str(1))


def test_get_text_containers(get_test_decision_standard_pdf_path):
    factory = corpus.BaseCorpusDocumentFactory(pdf=get_test_decision_standard_pdf_path)
    factory.pre_process()
    assert list(factory.get_text_containers([0]))


def test_from_pdf(get_test_decision_standard_pdf_path):
    assert corpus.BaseCorpusDocumentFactory.from_pdf(pdf=get_test_decision_standard_pdf_path)


def test_check_decision():
    assert corpus.BaseCorpusDocumentFactory.check_decision() is False
