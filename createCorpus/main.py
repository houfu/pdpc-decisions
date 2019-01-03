#  MIT License Copyright (c) 2019. Houfu Ang.

import os

from xpdf_python import to_text

from constants import SOURCE_FILE_PATH, PLAIN_CORPUS_FILE_PATH
from createCorpus.findCitation import find_citation


def get_text_pdf(filename):
    return to_text(filename, False)[0]


"""
Execute this code to prepare a distribution for the corpus. 

* Reads individual pdf files and transfers them to plain text format.
* Reads the plain text format to get the citation of the case.
"""

proceed = input('Do you wish to overwrite existing files in the corpus?')
fileList = []
for entry in os.scandir(SOURCE_FILE_PATH):
    if entry.name[-3:] == 'pdf':
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
