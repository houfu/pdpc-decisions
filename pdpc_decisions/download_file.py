#  MIT License Copyright (c) 2020. Houfu Ang

import io
import os
import re

import requests


def download_files(options, items):
    print('Start downloading files.')
    if not os.path.exists(options["download_folder"]):
        os.mkdir(options["download_folder"])
    for item in items:
        print("Downloading a File: ", item.download_url)
        print("Date of Decision: ", item.published_date)
        print("Respondent: ", item.respondent)
        if item.download_url[-3:] == 'pdf':
            download_pdf(options["download_folder"], item)
        else:
            download_text(options["download_folder"], item)
    print('Finished downloading files to ', options["download_folder"])


def download_pdf(download_folder, item):
    destination_filename = "{} {}.pdf".format(item.published_date.strftime('%Y-%m-%d'), item.respondent)
    destination = os.path.join(download_folder, destination_filename)
    with open(destination, 'wb') as file:
        pdf_file = requests.get(item.download_url).content
        file.write(pdf_file)
    print("Downloaded a pdf: ", destination)
    return destination


def download_text(download_folder, item):
    destination_filename = "{} {}.txt".format(item.published_date.strftime('%Y-%m-%d'),
                                              item.respondent)
    destination = os.path.join(download_folder, destination_filename)
    with open(destination, "w", encoding='utf-8') as f:
        f.writelines(get_text_stream(item))
    print("Downloaded a text: ", destination)
    return destination


def get_text_from_item(item):
    if item.download_url[-3:] == 'pdf':
        return clean_up_source(get_text_from_pdf(item))
    else:
        return get_text_stream(item)


def get_text_from_pdf(item):
    r = requests.get(item.download_url)
    with io.BytesIO(r.content) as pdf, io.StringIO() as output_string:
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.converter import TextConverter
        from pdfminer.layout import LAParams
        from pdfminer.pdfpage import PDFPage
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, codec='utf-8',
                               laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(pdf, check_extractable=True):
            interpreter.process_page(page)
        return output_string.getvalue()


def get_text_stream(item):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(requests.get(item.download_url).text, features='html5lib')
    rte = soup.find('div', class_='rte')
    text = rte.get_text()
    assert text, 'Download_text failed to get text from web page.'
    return text


def remove_extra_linebreaks(source):
    return [x for x in source if x != '' and not re.search(r'^\s+$', x)]


def remove_numbers_as_first_characters(source):
    return [x for x in source if not re.search(r'^\d*[\s.]*$', x)]


def remove_citations(source):
    return [x for x in source if not re.search(r'^\s+\[\d{4}]\s+(?:\d\s+)?[A-Z|()]+\s+\d+[\s.]?\s+$', x)]


def remove_feed_carriage(source):
    # identifies repeated instances (likely to be headers or footers)
    matches = [x for x in source if re.search(r'^\f', x)]
    counts = []
    for match in [ele for ind, ele in enumerate(matches, 1) if ele not in matches[ind:]]:
        counts.append((match, matches.count(match)))
    counts.sort(key=lambda m: m[1], reverse=True)
    if len(counts) > 1 and counts[0][1] > 1:
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
    if not os.path.exists(options["corpus_folder"]):
        os.mkdir(options["corpus_folder"])
    for item in items:
        print("Source File: ", item.download_url)
        print("Date of Decision: ", item.published_date)
        print("Respondent: ", item.respondent)
        destination_filename = "{} {}.txt".format(item.published_date.strftime('%Y-%m-%d'),
                                                  item.respondent)
        destination = os.path.join(options["corpus_folder"], destination_filename)
        with open(destination, 'w') as fOut:
            text = get_text_from_item(item)
            fOut.write(text)
        print("Wrote: {}".format(destination))
    print('Number of items in corpus: ', len(items))
    print('Finished creating corpus at ', options["corpus_folder"])
