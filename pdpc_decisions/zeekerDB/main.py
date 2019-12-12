#  MIT License Copyright (c) 2019. Houfu Ang.

import os

from pymongo import ReplaceOne, InsertOne, MongoClient

from constants import PLAIN_CORPUS_FILE_PATH


def get_text(filename):
    with open(filename, 'rb') as infile:
        return [x.strip().decode('utf-8') for x in infile.readlines()]


"""
Execute this code to write to the zeeker database 

"""

user = input('What is the name of the database user?')
password = input('What is {0}\'s password?'.format(user))
connection_string = "mongodb+srv://{user}:{pw}@zeeker-a1-otlvr.gcp.mongodb.net/test?retryWrites=true&w=majority" \
    .format(user=user, pw=password)
db_client = MongoClient(connection_string)
collection = db_client['pdpc-sg-decisions']['Singapore Data Protection Cases']

plain_source = input(
    'Insert path to plain corpus. Default: {0}'.format(PLAIN_CORPUS_FILE_PATH)) or '../dist/plain_corpus'
requests = []
for entry in os.scandir(plain_source):
    citation_file = entry.name[:-4]
    citation = citation_file.replace('_', ' ')
    if collection.find_one({'citation': citation}):
        requests.append(ReplaceOne({'citation': citation}, {
            'citation': citation,
            'text': get_text(entry.path)
        }))
    else:
        requests.append(InsertOne({
            'citation': citation,
            'text': get_text(entry.path)
        }))

result = collection.bulk_write(requests)
print('A total of {0} requests. {1} inserted. {2} updated. Success!'.format(len(requests), result.inserted_count,
                                                                            result.modified_count))
