#  MIT License Copyright (c) 2019. Houfu Ang.

import io
import os

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from constants import SOURCE_FILE_PATH, PLAIN_CORPUS_FILE_PATH
from createCorpus.findCitation import find_citation


def get_text_pdf(filename):
    output = io.StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)
    infile = open(filename, 'rb')
    for page in PDFPage.get_pages(infile):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    return text


"""
Execute this code to prepare a distribution for the corpus. 

* Reads individual pdf files and transfers them to plain text format.
* Reads the plain text format to get the citation of the case.
"""

proceed = input('Do you wish to overwrite existing files in the corpus?')
fileList = []
for entry in os.scandir(SOURCE_FILE_PATH):
    if entry.name[-3:] == 'pdf':
        print(entry.path)
        fileList.append(get_text_pdf(entry.path))

write_count = 0

for idx, f in enumerate(fileList):
    citation = find_citation(f)
    if citation:
        citation_file = citation.replace(' ', '_')
        file_path = PLAIN_CORPUS_FILE_PATH + citation_file + '.txt'
        if os.path.isfile(file_path):
            if proceed:
                with open(file_path, 'w') as fOut:
                    fOut.write(f)
                    print('Wrote: ', citation_file + '.txt')
                    write_count += 1
        else:
            with open(file_path, 'w') as fOut:
                fOut.write(f)
                print('Wrote: ', citation_file + '.txt')
                write_count += 1
    else:
        print('Citation not found: ', f[:60])

print('Wrote %d files' % write_count)
print('Success!')
