from pdpc_decisions.corpus_text.decision_v1 import DecisionV1Factory


def test_check_decision(decisions_corpus_gold):
    assert DecisionV1Factory.check_decision(decisions_corpus_gold[0]) is False
    assert DecisionV1Factory.check_decision(decisions_corpus_gold[1]) is True
    assert DecisionV1Factory.check_decision(decisions_corpus_gold[2]) is False


def test__DecisionV1Factory(decisions_corpus_gold):
    document = DecisionV1Factory.from_decision_item(decisions_corpus_gold[1])
    assert len(document.paragraphs) == 43
    assert document.paragraphs[19].paragraph_mark == '17.'
    assert document.paragraphs[
               15].text == 'However, rather than proceed with the printing of the annual premium statements,  ' \
                           'Toh-Shi  performed  further  processing  by  sorting  the  data according  to  postal  ' \
                           'code,  overseas  address  and  non-deliverable  mail before printing. It did so in ' \
                           'order to enjoy postage savings. Toh-Shi did not provide any UAT samples of the further ' \
                           'sorted data to Aviva for its verification  and  confirmation  before  printing  the  ' \
                           'annual  premium statements.'
    # Test footnotes
    assert document.paragraphs[41].text[900:950] == 'h of Section 24 of the PDPA (The  Commission’s dec'
