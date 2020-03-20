#  MIT License Copyright (c) 2020. Houfu Ang

import os

import pytest

import pdpc_decisions.download_file as download


def test_remove_extra_linebreaks():
    test_text = ['PERSONAL DATA PROTECTION COMMISSION ', '', 'Case No. DP-1810-B2869 ', '',
                 'In the matter of an investigation under section 50(1) of the  ', '',
                 'Personal Data Protection Act 2012 ', '', ' ', '', ' ', ' ', '1. ', '', 'And ', '', ' ', '',
                 'ERGO Insurance Pte. Ltd. ']
    gold_text = ['PERSONAL DATA PROTECTION COMMISSION ', 'Case No. DP-1810-B2869 ',
                 'In the matter of an investigation under section 50(1) of the  ',
                 'Personal Data Protection Act 2012 ', '1. ', 'And ', 'ERGO Insurance Pte. Ltd. ']
    result = download.remove_extra_linebreaks(test_text)
    assert result == gold_text


def test_remove_numbers_as_first_characters():
    test_text = ['PERSONAL DATA PROTECTION COMMISSION ', 'Case No. DP-1810-B2869 ',
                 'In the matter of an investigation under section 50(1) of the  ',
                 'Personal Data Protection Act 2012 ', '1. ', 'And ', 'ERGO Insurance Pte. Ltd. ']
    gold_text = ['PERSONAL DATA PROTECTION COMMISSION ', 'Case No. DP-1810-B2869 ',
                 'In the matter of an investigation under section 50(1) of the  ',
                 'Personal Data Protection Act 2012 ', 'And ', 'ERGO Insurance Pte. Ltd. ']
    result = download.remove_numbers_as_first_characters(test_text)
    assert result == gold_text


def test_remove_feed_carriage():
    test_text = ['when they were restarted, the Organisation’s employees had failed to follow the correct ',
                 'restart process. They were supposed to start both servers at the same time but this was ',
                 '\fnot done as the starting of the printer server initially failed. This resulted in documents '
                 'with duplicate document IDs being generated and hence the wrong documents being sent ',
                 '\f', '\fSearchAsia Consulting Pte. Ltd. ',
                 '\fSearchAsia Consulting Pte. Ltd. ', '\fSearchAsia Consulting Pte. Ltd. ']
    gold_text = ['when they were restarted, the Organisation’s employees had failed to follow the correct ',
                 'restart process. They were supposed to start both servers at the same time but this was ',
                 'not done as the starting of the printer server initially failed. This resulted in documents '
                 'with duplicate document IDs being generated and hence the wrong documents being sent ']
    result = download.remove_feed_carriage(test_text)
    assert result == gold_text


def test_remove_citations():
    test_text = [' [2019] SGPDPC 40 ', '3. ',
                 'The résumés uploaded to the Website were intended to only be accessible by ',
                 '[2016] SGPDPC 19 at [51]:  ', 'see Re Tutor City [2019] SGPDPC 5 at [16]. ']
    gold_text = ['3. ',
                 'The résumés uploaded to the Website were intended to only be accessible by ',
                 '[2016] SGPDPC 19 at [51]:  ', 'see Re Tutor City [2019] SGPDPC 5 at [16]. ']
    result = download.remove_citations(test_text)
    assert result == gold_text


def test_join_sentences_in_paragraph():
    test_text_1 = [
        'In  its  representations  to  the  Commission,  the  Organisation  stated  that  it  had ',
        'asked  the  Developer  whether  the  résumés  uploaded  to  the  Website  would  be ',
        'encrypted  and  the  Developer  responded  saying  that  “it  was  safe”.  This  does  not ',
        'detract  from  the  fact  that  the  Organisation  did  not  set  out  its  instructions  to  the ',
        'developer  in  writing.',
        'Therefore!'
    ]
    gold_text = [
        'In  its  representations  to  the  Commission,  the  Organisation  stated  that  it  had asked'
        '  the  Developer  whether  the  résumés  uploaded  to  the  Website  would  be encrypted  and  '
        'the  Developer  responded  saying  that  “it  was  safe”.  This  does  not detract  from  the  '
        'fact  that  the  Organisation  did  not  set  out  its  instructions  to  the developer  in  writing.',
        'Therefore!']
    result = download.join_sentences_in_paragraph(test_text_1)
    assert result == gold_text


def test_clean_up_source():
    test_text = 'PERSONAL DATA PROTECTION COMMISSION \n\nCase No. DP-1810-B2869 \n\n' \
                'In the matter of an investigation under section 50(1) of the  ' \
                '\n\nPersonal Data Protection Act 2012 \n\n \n\n \n \n1. \n\nAnd ' \
                '\n\n \n\nERGO Insurance Pte. Ltd. \n\n \n\nSUMMARY OF THE DECISION \n\n \n\n' \
                'ERGO  Insurance  Pte  Ltd  (the  “Organisation”)  is  a  general  insurer  and  operates' \
                '  an \n\ninternet portal (the “Portal”) which enables its insurance intermediaries, who are not ' \
                'the \n\nOrganisation’s employees, to request for documents of policyholders represented by the ' \
                '\n\nintermediaries. These documents contain the policyholders’ personal data such as ' \
                'their \n\nnames, addresses, car registration numbers, genders, nationalities, NRIC numbers, ' \
                'dates \n\nof birth and contact numbers (the “Personal Data”).  \n\n \n\n2. \n\nThe ' \
                'Organisation voluntarily informed the Personal Data Protection Commission on ' \
                '15 \n\nOctober  2018  that  it  had  earlier  discovered,  on  ' \
                '11  September  2018,  that  some  of  its \n\ninsurance intermediaries had been ' \
                'incorrectly sent documents of policyholders who were \n\nrepresented by other insurance ' \
                'intermediaries (the “Incident”). The Incident arose when \n\nsome  insurance  intermediaries  ' \
                '(the  “Intermediaries”)  requested  for  documents  of \n\npolicyholders  which  they  ' \
                'represent  through  the  Portal.  However,  the  Organisation’s \n\napplication and printer servers' \
                ' had been shut down for a scheduled system downtime and \n\nwhen they were restarted, ' \
                'the Organisation’s employees had failed to follow the correct \n\nrestart process. ' \
                'They were supposed to start both servers at the same time but this was \n\n\fnot done ' \
                'as the starting of the printer server initially failed. This resulted in documents \n\nwith ' \
                'duplicate document IDs being generated and hence the wrong documents being sent \n\nto the ' \
                'Intermediaries. As a result of the Incident, the Personal Data of 57 individuals were ' \
                '\n\nmistakenly disclosed to the Intermediaries. \n\n \n\n3. \n\n' \
                'The Personal Data Protection Commission found that the Organisation did not have in \n\nplace ' \
                ' a  clearly  defined  process  to  restart  its  application  and  printer  servers  and  ' \
                'a \n\nsufficiently  robust document  ID  generation process  (such  as including  a  timestamp  as ' \
                '\n\npart  of  the  document  ID)  to  prevent  the  duplication  of  document  IDs.  In  the ' \
                '\n\ncircumstances  the  Deputy  Commissioner  for  Personal  Data  Protection  found  the ' \
                '\n\nOrganisation  in  breach  of  section  24  of  the  Personal  Data  Protection  Act  2012  ' \
                'and \n\ndecided  to  give  a  warning  to  the  Organisation.  ' \
                'No  directions  are  required  as  the \n\nOrganisation  implemented  corrective  measures  that  ' \
                'addressed  the  gap  in  its  security \n\narrangements. \n\n \n\n\f'
    result = download.clean_up_source(test_text)
    gold_text = 'PERSONAL DATA PROTECTION COMMISSION Case No. DP-1810-B2869 ' \
                'In the matter of an investigation under section 50(1) of the  Personal Data Protection Act 2012 ' \
                'And ERGO Insurance Pte. Ltd. \n' \
                'SUMMARY OF THE DECISION ' \
                'ERGO  Insurance  Pte  Ltd  (the  “Organisation”)  is  a  general  insurer  and  operates' \
                '  an internet portal (the “Portal”) which enables its insurance intermediaries, who are not ' \
                'the Organisation’s employees, to request for documents of policyholders represented by the ' \
                'intermediaries. These documents contain the policyholders’ personal data such as ' \
                'their names, addresses, car registration numbers, genders, nationalities, NRIC numbers, ' \
                'dates of birth and contact numbers (the “Personal Data”).  \n' \
                'The Organisation voluntarily informed the Personal Data Protection Commission on ' \
                '15 October  2018  that  it  had  earlier  discovered,  on  11  September  2018,  that  ' \
                'some  of  its insurance intermediaries had been ' \
                'incorrectly sent documents of policyholders who were represented by other insurance ' \
                'intermediaries (the “Incident”). The Incident arose when some  insurance  intermediaries  ' \
                '(the  “Intermediaries”)  requested  for  documents  of policyholders  which  they  ' \
                'represent  through  the  Portal.  However,  the  Organisation’s application and printer servers' \
                ' had been shut down for a scheduled system downtime and when they were restarted, ' \
                'the Organisation’s employees had failed to follow the correct restart process. ' \
                'They were supposed to start both servers at the same time but this was not done ' \
                'as the starting of the printer server initially failed. This resulted in documents with ' \
                'duplicate document IDs being generated and hence the wrong documents being sent to the ' \
                'Intermediaries. As a result of the Incident, the Personal Data of 57 individuals were ' \
                'mistakenly disclosed to the Intermediaries. \n' \
                'The Personal Data Protection Commission found that the Organisation did not have in place ' \
                ' a  clearly  defined  process  to  restart  its  application  and  printer  servers  and  ' \
                'a sufficiently  robust document  ID  generation process  (such  as including  a  timestamp  as ' \
                'part  of  the  document  ID)  to  prevent  the  duplication  of  document  IDs.  In  the ' \
                'circumstances  the  Deputy  Commissioner  for  Personal  Data  Protection  found  the ' \
                'Organisation  in  breach  of  section  24  of  the  Personal  Data  Protection  Act  2012  ' \
                'and decided  to  give  a  warning  to  the  Organisation.  ' \
                'No  directions  are  required  as  the Organisation  implemented  corrective  measures  that  ' \
                'addressed  the  gap  in  its  security arrangements. '
    assert result == gold_text


def test_get_text_from_pdf(decisions_gold, get_test_pdf_url):
    decision = decisions_gold[0]
    decision.download_url = get_test_pdf_url
    assert download.get_text_from_pdf(decision)


def test_download_pdf(options_test, decisions_gold, get_test_pdf_url):
    if not os.path.exists(options_test["download_folder"]):
        os.mkdir(options_test["download_folder"])
    decision = decisions_gold[0]
    decision.download_url = get_test_pdf_url
    destination = ''
    try:
        destination = download.download_pdf(options_test['download_folder'], decision)
        assert destination == "{}{} {}.pdf".format(options_test['download_folder'], '2019-08-02',
                                                   'Avant Logistic Service')
        assert os.path.isfile(destination)
    finally:
        os.remove(destination)


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


def test_create_corpus(options_test, decisions_gold, get_test_txt_path, get_test_pdf_url):
    test_decisions = decisions_gold.copy()
    test_decisions[0].download_url = get_test_txt_path
    for idx in range(1, 5):
        test_decisions[idx].download_url = get_test_pdf_url
    try:
        download.create_corpus(options_test, test_decisions)
        gold_file_list = ['2019-08-02 Avant Logistic Service.txt', '2019-08-02 Genki Sushi.txt',
                          '2019-08-02 Championtutor.txt', '2019-08-02 CDP and Toppan Security Printing.txt',
                          '2019-08-02 Horizon Fast Ferry.txt']
        file_list = os.listdir(options_test['corpus_folder'])
        for file in gold_file_list:
            file_list.index(file)
            file_path = options_test['corpus_folder'] + file
            with open(file_path, 'r') as f:
                assert f.readlines()
    finally:
        import shutil
        shutil.rmtree(options_test['corpus_folder'])


@pytest.mark.skip('Implementation is still wonky.')
def test_get_text_stream(get_test_txt_path, decisions_gold):
    test_decisions = decisions_gold.copy()
    test_decisions[0].download_url = get_test_txt_path
    result = download.get_text_stream(test_decisions[0])
    gold_text = 'Breach of the Protection and Accountability Obligations by Global Outsource Solutions \n' \
                '05 Dec 2019 \n' \
                "Global Outsource Solutions was found in breach of the PDPA for failing to put in place " \
                "reasonable security arrangements to protect the personal data collected by its website " \
                "and for failing to develop and implement data protection policies. " \
                "This resulted in the disclosure of personal data of customers on the organisation’s " \
                "online warranty registration portal." \
                'Global Outsource Solutions was directed to develop and implement policies for ' \
                'data protection and staff training in data protection, ' \
                'and to put all employees handling personal data through such training.'
    assert result == gold_text
