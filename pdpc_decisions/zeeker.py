#  MIT License Copyright (c) 2019. Houfu Ang
import os
import re
import urllib.parse
from urllib.request import urlopen

import wget
from bs4 import BeautifulSoup
from pymongo import MongoClient, DeleteMany, InsertOne

from download_file import get_text_from_pdf, clean_up_source


def zeeker_db_build(options, items):
    print('Start zeeker database construction.')
    password = urllib.parse.quote_plus(input('What is {0}\'s password?'.format('houfu')))
    connection_string = "mongodb+srv://houfu:{pw}@zeeker-a2-otlvr.gcp.mongodb.net/test?retryWrites=true&w" \
                        "=majority".format(pw=password)
    db_client = MongoClient(connection_string)
    data_collection = db_client['pdpc-decisions']['decisions']
    print("Deleting ALL contents of database.")
    requests = [DeleteMany({})]
    for item in items:
        requests.append(InsertOne(vars(item)))
        print('Updated: ', item)
    data_collection.bulk_write(requests, bypass_document_validation=True)
    print('Inserted {} documents in database.'.format(len(requests) - 1))
    print('Creating corpus in zeeker database.')
    corpus_collection = db_client['pdpc-decisions']['corpus']
    requests = [DeleteMany({})]
    download_search_results = data_collection.find({}, {'_id': 1, 'download_url': 1})
    print('Start downloading files.')
    if not os.path.exists(options["download_folder"]):
        os.mkdir(options["download_folder"])
    for doc in download_search_results:
        url = doc['download_url']
        print("Downloading a File: ", url)
        if url[-3:] == 'pdf':
            destination = "{}zeeker_temp.pdf".format(options["download_folder"])
            wget.download(url, out=destination)
            print("Downloaded a pdf: ", destination)
            text = clean_up_source(get_text_from_pdf(destination))
            requests.append(InsertOne({'_id': doc['_id'], 'text': text}))
            print('Inserted: ', doc['_id'])
            os.remove(destination)
        else:
            print('Reading a text file: ', url)
            soup = BeautifulSoup(urlopen(url), 'html5lib')
            source_text = soup.find('div', class_='rte').getText()
            lines = [line + '\n' for line in re.split(r"\n\s+", source_text) if line != '']
            text = ''.join(lines)
            requests.append(InsertOne({'_id': doc['_id'], 'text': text}))
            print('Inserted: ', doc['_id'])
    corpus_collection.bulk_write(requests)
    print('Inserted {} documents in corpus.'.format(len(requests) - 1))
