#  MIT License Copyright (c) 2019. Houfu Ang

import io
import os
import re
import shutil

import wget
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


def download_files(options, items):
    print('Start downloading files.')
    if not os.path.exists(options["download_folder"]):
        os.mkdir(options["download_folder"])
    for item in items:
        url = item.download_url
        print("Downloading a File: ", url)
        print("Date of Decision: ", item.date)
        print("Respondent: ", item.respondent)
        if url[-3:] == 'pdf':
            destination = "{}{} {}.pdf".format(options["download_folder"], item.date.strftime('%Y-%m-%d'),
                                               item.respondent)
            wget.download(url, out=destination)
            print("Downloaded a pdf: ", destination)
        else:
            destination = "{}{} {}.txt".format(options["download_folder"], item.date.strftime('%Y-%m-%d'),
                                               item.respondent)
            with open(destination, "w", encoding='utf-8') as f:
                from bs4 import BeautifulSoup
                from urllib.request import urlopen
                soup = BeautifulSoup(urlopen(url), 'html5lib')
                text = soup.find('div', class_='rte').getText()
                lines = re.split(r"\n\s+", text)
                f.writelines([line + '\n' for line in lines if line != ""])
            print("Downloaded a text: ", destination)
    print('Finished downloading files to ', options["download_folder"])


def get_text_from_pdf(filename):
    output = io.StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    try:
        interpreter = PDFPageInterpreter(manager, converter)
        with open(filename, 'rb') as infile:
            for page in PDFPage.get_pages(infile):
                interpreter.process_page(page)
        text = output.getvalue()
    finally:
        converter.close()
        output.close()
    return text


def remove_extra_linebreaks(source):
    return [x for x in source if x != '' and not re.search(r'^\s+$', x)]


def remove_numbers_as_first_characters(source):
    return [x for x in source if not re.search(r'^\d*[\s.]*$', x)]


def remove_citations(source):
    return [x for x in source if not re.search(r'^\s+\[\d{4}]\s+(?:\d\s+)?[A-Z|()]+\s+\d+[\s.]?\s+$', x)]


def remove_feed_carriage(source):
    # identifies repeated instances (likely to be headers or footers
    matches = [x for x in source if re.search(r'^\f', x)]
    counts = []
    for match in [ele for ind, ele in enumerate(matches, 1) if ele not in matches[ind:]]:
        counts.append((match, matches.count(match)))
    counts.sort(key=lambda match: match[1], reverse=True)
    if counts[0][1] > 1:
        return [x.replace('\f', '') for x in source if x != '\f' and x != counts[0][0]]
    else:
        return [x.replace('\f', '') for x in source if x != '\f']


def join_sentences_in_paragraph(source):
    result = []
    paragraph_string = ''
    for x in source:
        if re.search(r'\.\s*$', x):
            paragraph_string += x
            result.append(paragraph_string)
            paragraph_string = ''
        else:
            paragraph_string += x
    if paragraph_string != '':
        result.append(paragraph_string)
    return result


def clean_up_source(text):
    text_lines = text.split('\n')
    start_count = len(text_lines)
    text_lines = remove_extra_linebreaks(text_lines)
    text_lines = remove_numbers_as_first_characters(text_lines)
    text_lines = remove_citations(text_lines)
    text_lines = remove_feed_carriage(text_lines)
    text_lines = join_sentences_in_paragraph(text_lines)
    end_count = len(text_lines)
    reduced = (start_count - end_count) / start_count * 100
    print('Reduced from {} lines to {} lines. {:0.2f}% Wow'.format(start_count, end_count, reduced))
    return '\n'.join(text_lines)


def create_corpus(options, items):
    print('Now creating corpus.')
    file_count = len(list(os.scandir(options["download_folder"])))
    if file_count != len(items):
        print('Create corpus needs to download all files to start.')
        if file_count != 0:
            print("There are existing items. They will be cleared before we start downloading.")
            shutil.rmtree(options["download_folder"])
            os.mkdir(options["download_folder"])
        download_files(options, items)
    if not os.path.exists(options["corpus_folder"]):
        os.mkdir(options["corpus_folder"])
    file_list = os.scandir(options["download_folder"])
    for entry in file_list:
        print('Now processing: {}'.format(entry.name))
        file_name = options["corpus_folder"] + entry.name[:-4] + '.txt'
        if entry.name[-3:] == 'pdf':
            with open(file_name, 'w', encoding='utf-8') as fOut:
                fOut.write(clean_up_source(get_text_from_pdf(entry.path)))
                print("Wrote: {}".format(file_name))
        if entry.name[-3:] == 'txt':
            shutil.copy(entry.path, file_name)
            print("Copied: {}".format(file_name))
