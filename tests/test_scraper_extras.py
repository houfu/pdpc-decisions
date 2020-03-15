#  MIT License Copyright (c) 2020. Houfu Ang
import pdpc_decisions.scraper_extras as extras


def test_get_enforcement(decisions_gold):
    extras.get_enforcement(decisions_gold)
    assert decisions_gold[0].enforcement == ['directions']
    assert decisions_gold[1].enforcement == [['financial', 54000]]
    assert decisions_gold[2].enforcement == [['financial', 16000]]
    assert decisions_gold[3].enforcement == [['financial', 5000]]
    assert decisions_gold[4].enforcement == [['financial', 24000], ['financial', 12000]]


def test_get_decision_citation(decisions_gold):
    extras.get_decision_citation(decisions_gold)
    assert decisions_gold[0].citation == '[2020] SGPDPC 1'
    assert decisions_gold[0].case_number == 'DP-1811-B3058'
