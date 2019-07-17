#  MIT License Copyright (c) 2019. Houfu Ang.

import io
import os

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from constants import SOURCE_FILE_PATH, PLAIN_CORPUS_FILE_PATH
from createCorpus.cleanUpSource import clean_up_source
from createCorpus.findCitation import find_citation


def get_first_text_pdf(filename):
    output = io.StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)
    infile = open(filename, 'rb')
    for page in PDFPage.get_pages(infile, maxpages=1):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    return text


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
        first_page = get_first_text_pdf(entry.path)
        citation = find_citation(first_page)
        fileList.append((citation, entry.path))

write_count = 0

for idx, f in enumerate(fileList):
    citation = f[0]
    if citation:
        citation_file = citation.replace(' ', '_')
        file_path = PLAIN_CORPUS_FILE_PATH + citation_file + '.txt'
        if os.path.isfile(file_path):
            if proceed:
                print('Now processing: {0}'.format(f[0]))
                with open(file_path, 'w') as fOut:
                    fOut.write(clean_up_source(get_text_pdf(f[1])))
                    print('Wrote: ', citation_file + '.txt')
                    write_count += 1
        else:
            print('Now processing: {0}'.format(f[0]))
            with open(file_path, 'w') as fOut:
                fOut.write(clean_up_source(get_text_pdf(f[1])))
                print('Wrote: ', citation_file + '.txt')
                write_count += 1
    else:
        print('Citation not found: ', f[2])

print('Wrote %d files' % write_count)
print('Success!')
