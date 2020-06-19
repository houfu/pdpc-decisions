from pdpc_decisions.corpus_text.decision_v2 import DecisionV2Factory


def test_process_all(decisions_corpus_gold):
    document = DecisionV2Factory.from_decision_item(decisions_corpus_gold[0])
    assert document


def test_check_decision(decisions_corpus_gold):
    assert DecisionV2Factory.check_decision(decisions_corpus_gold[0]) is True
    assert DecisionV2Factory.check_decision(decisions_corpus_gold[1]) is False
    assert DecisionV2Factory.check_decision(decisions_corpus_gold[2]) is False
