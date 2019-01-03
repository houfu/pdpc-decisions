# pdpc-decisions
PDPC Decisions Corpus is a corpus of decisions released by the Personal Data Protection Commission of Singapore 
at <https://www.pdpc.gov.sg/Commissions-Decisions/Data-Protection-Enforcement-Cases>.

Note the [conditions of the use of the source material](./LICENSE). Use of the source material for commercial purposes 
is expressly prohibited.

## How to use PDPC Decisions Corpus
1. See releases for an archive of decisions. Each plain text contains 1 decision separated by line breaks denoting 
paragraphs. Paragraphs beginning with `^` are footnotes. The footnote refers to the point in the text labelled with 
`^`.

2.  Consider using the [DecisionTokenizer class](./tagging/DecisionTokenizer.py) to tokenize the text. The class 
uses custom tokenizers created for this corpus.

3. Consider using the [PDPCDecisionCorpus class](./PDPCDecisionCorpus.py) for reading the corpus. 
(Note that the [DecisionTokenizer class](./tagging/DecisionTokenizer.py) is a dependency if you intend to cut 
and paste the code.) 
The reader uses a similar interface as the 
[NLTK PlaintextCorpusReader](http://www.nltk.org/api/nltk.corpus.reader.html#nltk.corpus.reader.plaintext.PlaintextCorpusReader) 
but uses custom tokenizers created for the text. (NLTK is also required)

## Future Plans
Take a look at the [TODO](./TODO.md).

## Contact

Feel free to let me have your suggestions, comments or issues using the issue tracker or by 
[emailing me](mailto:houfu@outlook.sg).

It would also be nice to hear how you have used this corpus by using the above contacts. 