#  MIT License Copyright (c) 2019. Houfu Ang
import os
import re
import urllib.parse
from urllib.request import urlopen

import wget
from bs4 import BeautifulSoup
from pymongo import MongoClient, DeleteMany, InsertOne, UpdateOne

from pdpc_decisions.download_file import get_text_from_pdf, clean_up_source


def get_text(url, options):
    if url[-3:] == 'pdf':
        destination = "{}zeeker_temp.pdf".format(options["download_folder"])
        try:
            if not os.path.exists(options["download_folder"]):
                os.mkdir(options["download_folder"])
            wget.download(url, out=destination)
            print("Downloaded a pdf: ", destination)
            return clean_up_source(get_text_from_pdf(destination))
        finally:
            os.remove(destination)
    else:
        print('Reading a text file: ', url)
        soup = BeautifulSoup(urlopen(url), 'html5lib')
        source_text = soup.find('div', class_='rte').getText()
        lines = [line + '\n' for line in re.split(r"\n\s+", source_text) if line != '']
        return ''.join(lines)


def zeeker_db_build(options, items):
    print('Start zeeker database construction.')
    db_client = MongoClient(options['connection_string'])
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
    for doc in download_search_results:
        url = doc['download_url']
        print("Downloading a File: ", url)
        requests.append(InsertOne({'_id': doc['_id'], 'text': get_text(url, options)}))
        print('Inserted: ', doc['_id'])
    corpus_collection.bulk_write(requests)
    print('Inserted {} documents in corpus.'.format(len(requests) - 1))


def zeeker_db_update(options, items):
    print('Start updating zeeker database')
    db_client = MongoClient(options['connection_string'])
    data_collection = db_client['pdpc-decisions']['decisions']
    corpus_collection = db_client['pdpc-decisions']['corpus']
    data_requests = []
    corpus_requests = []
    for item in items:
        result = data_collection.find_one(
            {'date': item.date, 'download_url': item.download_url, 'respondent': item.respondent},
            projection={"_id": 1, "download_url": 1}
        )
        if result:
            data_requests.append(UpdateOne({'_id': result['_id']}, {'$set': vars(item)}))
            corpus_requests.append(
                UpdateOne({'_id': result['_id']},
                          {'$set': {'text': get_text(url=result['download_url'], options=options)}}))
        else:
            print('Inserting new item in data collection:', item)
            result = data_collection.insert_one(vars(item))
            corpus_requests.append(UpdateOne({'_id': result.inserted_id},
                                             {'$set': {'text': get_text(url=item.download_url, options=options)}}))
    data_collection.bulk_write(data_requests)
    print('Updated {} documents in database.'.format(len(data_requests) - 1))
    corpus_collection.bulk_write(corpus_requests)
    print('Updated {} documents in corpus.'.format(len(corpus_requests) - 1))


def zeeker_main(options, items):
    print('Start zeeker database options')
    password = urllib.parse.quote_plus(input('What is {0}\'s password?'.format('houfu')))
    options['connection_string'] = "mongodb+srv://houfu:{pw}@zeeker-a2-otlvr.gcp.mongodb.net/test?retryWrites=true&w" \
                                   "=majority".format(pw=password)
    if options['sub-action'] and options['sub-action'].lower() == 'build':
        zeeker_db_build(options, items)
    else:
        print('If sub-action is not "build", script will update database')
        zeeker_db_update(options, items)
