#  MIT License Copyright (c) 2020. Houfu Ang

import os

import pdpc_decisions.download_file as download


def test_get_text_from_pdf(decisions_corpus_gold):
    decision = decisions_corpus_gold[0]
    assert download.get_text_from_pdf(decision)
    decision = decisions_corpus_gold[1]
    assert download.get_text_from_pdf(decision)


def test_download_pdf(options_test, decisions_gold):
    if not os.path.exists(options_test["download_folder"]):
        os.mkdir(options_test["download_folder"])
    decision = decisions_gold[0]
    try:
        destination = download.download_pdf(options_test['download_folder'], decision)
        assert destination == f"{options_test['download_folder']}{'2019-08-02'} {'Avant Logistic Service'}.pdf"
        assert os.path.isfile(destination)
        destination_2 = download.download_pdf(options_test['download_folder'], decision)
        destination = f"{options_test['download_folder']}{'2019-08-02'} {'Avant Logistic Service'} (1).pdf"
        assert os.path.isfile(destination)
        assert destination_2 == f"{options_test['download_folder']}{'2019-08-02'} {'Avant Logistic Service'} (2).pdf"
        assert os.path.isfile(destination_2)
        download.download_pdf(options_test['download_folder'], decision)
        assert os.path.isfile(
            os.path.join(options_test['download_folder'], f"{'2019-08-02'} {'Avant Logistic Service'} (3).pdf"))
    finally:
        import shutil
        shutil.rmtree(options_test['download_folder'])


def test_download_text(options_test, decisions_gold, get_test_txt_path):
    if not os.path.exists(options_test["download_folder"]):
        os.mkdir(options_test["download_folder"])
    decision = decisions_gold[0]
    decision.download_url = get_test_txt_path
    destination = ''
    try:
        destination = download.download_text(options_test['download_folder'], decision)
        assert destination == "{}{} {}.txt".format(options_test['download_folder'], '2019-08-02',
                                                   'Avant Logistic Service')
        assert os.path.isfile(destination)
        with open(destination, 'r') as file:
            assert file.readlines()
    finally:
        os.remove(destination)
        os.rmdir(options_test["download_folder"])


def test_download_files(options_test, decisions_gold, get_test_txt_path, get_test_pdf_url, mocker):
    test_decisions = decisions_gold.copy()
    test_decisions[0].download_url = get_test_txt_path
    for idx in range(1, 5):
        test_decisions[idx].download_url = get_test_pdf_url
    try:
        download.download_files(options_test, test_decisions)
        file_list = os.listdir(options_test['download_folder'])
        file_list.index('2019-08-02 Avant Logistic Service.txt')
        file_list.index('2019-08-02 Genki Sushi.pdf')
        file_list.index('2019-08-02 Championtutor.pdf')
        file_list.index('2019-08-02 CDP and Toppan Security Printing.pdf')
        file_list.index('2019-08-02 Horizon Fast Ferry.pdf')
    finally:
        import shutil
        shutil.rmtree(options_test['download_folder'])

    mkdir_func = mocker.patch.object(os, 'mkdir')
    download.download_files(options_test, [])
    mkdir_func.assert_called()
