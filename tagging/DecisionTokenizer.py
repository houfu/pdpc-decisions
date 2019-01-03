
#  MIT License Copyright (c) 2019. Houfu Ang.

import re

from nltk import PunktSentenceTokenizer
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.api import TokenizerI
from nltk.tokenize.mwe import MWETokenizer


class DecisionTokenizer(TokenizerI):
    """
    Custom class to tokenize documents for the PDPC Decision Corpus .
    """

    def __init__(self):
        mwe_tokens = [
            # Common phrases that appear in Decisions, which meaning cannot be easily deciphered by:
            # (i) a dictionary from its words alone
            # (ii) common terms for which a shorthand would be useful for the compiler
            ('Deputy', 'Commissioner'),
            ('Grounds', 'of', 'Decision'),
            ('Information', "Commissioner's", 'Office'),
            ('Information', '&', 'Privacy', 'Commissioner', 'for', 'British', 'Columbia'),
            ('Office', 'of', 'the', 'Australian', 'Information', 'Commissioner'),
            ('Office', 'of', 'the', 'Privacy', 'Commissioner', 'of', 'Canada'),
            ('Personal', 'Data', 'Protection', 'Commission'),
            ('Personal', 'Data', 'Protection', 'Act', '2012'),
            ('Personal', 'Data', 'Protection', 'Act'),
            ('Personal', 'Data', 'Protection', 'Ordinance'),
            ('Personal', 'Data', '(Privacy)', 'Ordinance'),
            # Latin Weirdness
            ('inter', 'alia'),
        ]
        self.mwe_tokenizer = MWETokenizer(mwe_tokens)
        self.sent_tokenizer = PunktSentenceTokenizer()
        pattern = r'''(?x)
            \[\d{4}]\s+(?:\d\s+)?[A-Z|()]+\s+\d+  # Citations ([2018] SGPDPC 7)
        |   (?i)(?:section|clause)\s+\d+(?:\(\S+\))* # Section references (Section 24 etc)
        |   \d{1,3},(?:\d{3},)*\d{3}(?:\.\d)?  # >3 digit numbers separated by commas
        |   (?:\w+)?\$\d{1,3},(?:\d{3},)*\d{3}(?:\.\d{1,2})?  # >3 digit money with cents
        |   (?:\w+)?\$\d{1,3}(?:\.\d{1,2})?  # <3 digit money with cents
        |   \[\d+(?:\.\w+)*]  # Paragraph references ([14])
        |   \(\w+\)  # Sub paragraphs ((a), (1), (i) etc)
        |   \w+\'s\b  # Possessive nouns
        |   \w+s\'\B  # The other Possessive noun
        |   \^\d+  # Footnote notation
        |   \w+(?:\.\w*)*  # Paragraph numbers (12, 12., a. , b)
        # URLS
        |   <?(?:http|ftp|https)://[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-.,@?^=%&amp;:/~+#]*[\w\-@?^=%&amp;/~+#])?>?
        |   ^\d+%  # Percentages
        |   (?i)\d*(?:1st|2nd|3rd|[4-9]th|0th|11th|12th|13th)  # Ordinal numbers
        |   \w+(?:-\w+)* # Words
        |   [^\w\s]+  # Punctuation
        '''
        self.reg_tokenizer = RegexpTokenizer(pattern)
        self.regex_pte = re.compile(r'\bpte\.\B', flags=re.IGNORECASE)
        self.regex_ltd = re.compile(r'\bltd\.\B', flags=re.IGNORECASE)
        self.regex_no = re.compile(r'\bno\.\B', flags=re.IGNORECASE)
        self.regex_fn1 = re.compile(r'(?<=[A-Za-z]{3})[.,](?:\^)?(\d+)\s')
        self.regex_fn2 = re.compile(r'(?<=[A-Za-z]{3})(?:\^)?(\d+)\s')
        self.regex_page_no1 = re.compile(r'\n\d+\n')
        self.regex_page_no2 = re.compile(r'\nPage \d+ of \d+')

    def tokenize(self, s):
        return self.words(s)

    def tokenize_sents(self, strings):
        return [self.tokenize(s) for s in strings]

    def words(self, text, pre_process=True):
        if pre_process:
            text = self.pre_process_text(text)
        return self.mwe_tokenizer.tokenize(self.reg_tokenizer.tokenize(text))

    def sentences(self, text, pre_process=True):
        if pre_process:
            text = self.pre_process_text(text)
        return [self.words(sentence, pre_process=False) for sentence in self.sent_tokenizer.sentences_from_text(text)]

    def paragraphs(self, text):
        return [self.sentences(paragraph) for paragraph in text.split('\n')]

    def pre_process_text(self, text):
        """
        This is a internal function which 'cleans' up the text before it is tokenized by the custom regular expression
        tokenizer.
        :param text:
        :return:
        """
        res_text = text
        # Replace Pte. Ltd. with Pte Ltd (the extra punctuation confuses the sentence tokeniser
        res_text = re.sub(self.regex_pte, 'PTE ', res_text)
        res_text = re.sub(self.regex_ltd, 'LTD ', res_text)
        # For footnote notation, if notation is behind a full stop/end of sentence, to bring it back to the sentence
        res_text = re.sub(self.regex_fn1, r' ^\g<1>.', res_text)
        # For footnote notation, if the notation is stuck to a word, to split it
        res_text = re.sub(self.regex_fn2, r' ^\g<1>', res_text)
        # Convert No. to number
        res_text = re.sub(self.regex_no, 'Number ', res_text)
        # Remove lonely page Numbers
        res_text = re.sub(self.regex_page_no1, '', res_text)
        res_text = re.sub(self.regex_page_no2, '', res_text)
        # Expand contractions
        res_text = re.sub(r"\'ve", " have ", res_text)
        res_text = re.sub(r"can't", "cannot ", res_text)
        res_text = re.sub(r"n't", " not ", res_text)
        res_text = re.sub(r"I'm", "I am", res_text)
        res_text = re.sub(r"\'re", " are ", res_text)
        res_text = re.sub(r"\'d", " would ", res_text)
        res_text = re.sub(r"\'ll", " will ", res_text)
        # Expand short forms
        res_text = re.sub(r'e\.g\.', "for example", res_text, re.IGNORECASE)
        res_text = re.sub(r'i\.e\.', 'that is', res_text, re.IGNORECASE)
        res_text = re.sub(r'p\.|pg\.', 'page', res_text, re.IGNORECASE)
        res_text = re.sub(r'[iI]bid\.', 'ibid', res_text)
        return res_text

    def span_tokenize(self, s):
        pass


def _test_tokenize(text, file='tmp/text1.txt'):
    tokenizer = DecisionTokenizer()
    with open(file, 'w') as f:
        for paragraph in tokenizer.paragraphs(text):
            print(paragraph, file=f)


def words_tokenize(text):
    """
    Helper function to tokenize a text into words using custom tokenizer.
    :param text: The text to be tokenized.
    :return: list[string] The tokenized text.
    """
    tokenizer = DecisionTokenizer()
    return tokenizer.words(text)


def sents_tokenize(text):
    """
    Helper function which tokenize text into sentences, and then tokenizes the words in each sentence.
    :param text: The text to be tokenized.
    :return: list[[string]] The tokenized text.
    """
    tokenizer = DecisionTokenizer()
    return tokenizer.sentences(text)


def paras_tokenize(text):
    """
    Helper function which tokenize text into paragraphs, and then tokenizes the sentences in each paragraph,
    and then tokenizes the words in each sentence.

    The paragraphs are assumed to be split using new lines in the text.

    :param text:
    :return:
    """
    tokenizer = DecisionTokenizer()
    return tokenizer.paragraphs(text)
