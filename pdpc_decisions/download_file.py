#  MIT License Copyright (c) 2020. Houfu Ang
import io
import logging
import os
from typing import Iterable

import requests

from pdpc_decisions.classes import Options, PDPCDecisionItem, PDFFile

logger = logging.getLogger(__name__)


def download_files(options: Options, items: Iterable[PDPCDecisionItem]):
    logger.info('Start downloading files.')
    if not os.path.exists(options["download_folder"]):
        os.mkdir(options["download_folder"])
    for item in items:
        logger.info(f"Downloading {item}: {item.download_url}")
        if check_pdf(item.download_url):
            download_pdf(options["download_folder"], item)
        else:
            download_text(options["download_folder"], item)
    logger.info(f'Finished downloading files to {options["download_folder"]}')


def check_pdf(download_url: str) -> bool:
    """Check if the download_url is a PDF or not by reading the extension."""
    from urllib.parse import urlparse
    result = urlparse(download_url)
    return result.path[-3:] == 'pdf'


def download_pdf(download_folder: str, item: PDPCDecisionItem) -> str:
    """Downloads a pdf in the item to the download folder. Returns the path where the file is saved."""
    destination = os.path.join(download_folder,
                               f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent}.pdf")
    if os.path.isfile(os.path.join(download_folder,
                                   f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} (1).pdf")):
        logger.warning('Found secondary format for PDF files. To follow format for this file.')
        file_num = 2
        destination = os.path.join(download_folder,
                                   f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} ({file_num}).pdf")
        while os.path.isfile(destination):
            file_num += 1
            destination = os.path.join(download_folder,
                                       f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} ({file_num}).pdf")
    if os.path.isfile(destination):
        logger.warning('Found two decisions with the same PDF output file name. Rewriting to secondary format.')
        file_num = 1
        os.rename(destination,
                  os.path.join(download_folder,
                               f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} ({file_num}).pdf"))
        file_num += 1
        destination = os.path.join(download_folder,
                                   f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} ({file_num}).pdf")
    with open(destination, 'wb') as file:
        pdf_file = requests.get(item.download_url).content
        file.write(pdf_file)
    logger.info(f"Downloaded a pdf: {destination}")
    return destination


def download_text(download_folder: str, item: PDPCDecisionItem) -> str:
    """Downloads a text file in the item to the download folder. Returns the path where the file is saved."""
    destination_filename = "{} {}.txt".format(item.published_date.strftime('%Y-%m-%d'),
                                              item.respondent)
    destination = os.path.join(download_folder, destination_filename)
    with open(destination, "w", encoding='utf-8') as f:
        f.writelines(get_text_stream(item))
    logger.info(f"Downloaded a text: {destination}")
    return destination


def get_text_from_pdf(source: PDPCDecisionItem, options: Options = None) -> str:
    """
    Gets text from the decision of source in PDF. Avoids the first page if it is a cover page.
    :param options:
    :param source:
    :return:
    """
    r = requests.get(source.download_url)
    from pdfminer.high_level import extract_text_to_fp
    from pdfminer.layout import LAParams
    with PDFFile(source, options) as pdf, io.StringIO() as output_string, io.StringIO() as test_string:
        params = LAParams(line_margin=2)
        extract_text_to_fp(pdf, test_string, page_numbers=[0])
        first_page = test_string.getvalue()
        if len(first_page.split()) > 100:
            extract_text_to_fp(pdf, output_string, laparams=params)
        else:
            from pdfminer.pdfpage import PDFPage
            pages = len([page for page in PDFPage.get_pages(pdf)])
            extract_text_to_fp(pdf, output_string, page_numbers=[i for i in range(pages)[1:]], laparams=params)
        return output_string.getvalue()


def get_text_stream(item):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(requests.get(item.download_url).text, features='html5lib')
    rte = soup.find('div', class_='rte')
    text = rte.get_text()
    assert text, 'Download_text failed to get text from web page.'
    return text
