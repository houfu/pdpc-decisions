from pdpc_decisions.corpus_text.summary import SummaryDecisionFactory


def test_get_decision(decisions_corpus_gold):
    document = SummaryDecisionFactory.from_decision_item(decisions_corpus_gold[2])
    assert len(document.paragraphs) == 5
    assert document.paragraphs[0].paragraph_mark == '1.'
    assert document.paragraphs[
               4].text == 'No directions are required as the Organisation has implemented corrective measures that ' \
                          'addressed the gaps in its security arrangements.'


def test_check_decision(decisions_corpus_gold):
    assert SummaryDecisionFactory.check_decision(decisions_corpus_gold[0]) is False
    assert SummaryDecisionFactory.check_decision(decisions_corpus_gold[1]) is False
    assert SummaryDecisionFactory.check_decision(decisions_corpus_gold[2]) is True
