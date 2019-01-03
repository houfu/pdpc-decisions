# TODO

###CreateCorpus
~~* ~~Rename filenames to something more sensible~~~~
* ~~Be able to update corpus without rebuilding the others~~
* (feat) Remove page numbers, page headers from corpus (Currently being done manually)
* (feat) Fix paragraphs that run over a page (Currently being done manually)
* (feat) Merge bullet points to the parent paragraph (Currently being done manually)
* (feat) Be able to tell the computer what words are emphasised in a quotation (useful for context) 
* ~~(feat) Where footnotes were used, to splice them from the referring word /~~ 
* (bug) Use a standard notation for footnotes (\^ instead of \[]) 
* (chore) Automatically copy LICENSE file to distribution
* (chore) Automatically zip the contents for distribution

### Tokenizer
* ~~(bug) Computer thinks Pte. is the end of the sentence. Cannot use Regex to process if they are on separate sentences~~
* ~~(bug) Depending on how the footnote is placed, may be at the end of the sentence (usually ok) or beginning of the sentence (not ok)~~

###Indexer
- [] Create a list where case information and summary is available