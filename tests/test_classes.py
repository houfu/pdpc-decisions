from pdpc_decisions import classes


def test_pdpcdecision_item_str(decisions_test_items):
    assert str(decisions_test_items[1][0]) == "PDPCDecisionItem: 2016-04-21 Institution of Engineers, Singapore"


def test_get_text_as_paragraphs(decisions_gold):
    document = classes.CorpusDocument(decisions_gold[0])
    document.paragraphs = [
        classes.Paragraph('This is the first paragraph.', '1.'),
        classes.Paragraph('This is the second paragraph.', '2.'),
        classes.Paragraph('This is the third paragraph.', '3.')
    ]
    assert document.get_text_as_paragraphs() == ['This is the first paragraph.',
                                                 'This is the second paragraph.',
                                                 'This is the third paragraph.']
    assert document.get_text_as_paragraphs(True) == ['1. This is the first paragraph.',
                                                     '2. This is the second paragraph.',
                                                     '3. This is the third paragraph.']
    assert document.get_text() == 'This is the first paragraph. ' \
                                  'This is the second paragraph. ' \
                                  'This is the third paragraph.'
    assert document.get_text(True) == '1. This is the first paragraph. ' \
                                      '2. This is the second paragraph. ' \
                                      '3. This is the third paragraph.'


def test_paragraph():
    test = classes.Paragraph('ABCDFEF G', '1.')
    assert str(test) == 'Paragraph: 1. ABCDFEF G'
    test = classes.Paragraph('ABCDFEG')
    assert str(test) == 'Paragraph: ABCDFEG'


def test_corpus_document(decisions_gold):
    test = classes.CorpusDocument()
    assert str(test) == "CorpusDocument:0, source: None"
    document = classes.CorpusDocument(decisions_gold[0])
    assert str(document) == "CorpusDocument:0, source: Avant Logistic Service, 2019-08-02"
