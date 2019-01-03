
#  MIT License Copyright (c) 2019. Houfu Ang.

from nltk.corpus import PlaintextCorpusReader

from tagging.DecisionTokenizer import DecisionTokenizer


class PDPCDecisionCorpus(PlaintextCorpusReader):
    """
    Custom class to read the documents in the corpus using the custom tokenizers written for this corpus.
    Interface inherits from/similar to nltk's PlainttextCorpusReader.
    """
    def __init__(self, root, fileids):
        super().__init__(root=root, fileids=fileids, word_tokenizer=DecisionTokenizer(),
                         sent_tokenizer=DecisionTokenizer())
