#  MIT License Copyright (c) 2020. Houfu Ang
import logging
import os
from typing import Sequence, List, Type

from pdpc_decisions.classes import Options, PDPCDecisionItem, CorpusDocument
from pdpc_decisions.corpus_text.basic import BasicCorpusFactory
from pdpc_decisions.corpus_text.common import BaseCorpusDocumentFactory
from pdpc_decisions.corpus_text.decision_v1 import DecisionV1Factory
from pdpc_decisions.corpus_text.decision_v2 import DecisionV2Factory
from pdpc_decisions.corpus_text.summary import SummaryDecisionFactory

logger = logging.getLogger(__name__)

factory_list: List[Type[BaseCorpusDocumentFactory]] = \
    [SummaryDecisionFactory, DecisionV1Factory, DecisionV2Factory, BasicCorpusFactory]


def get_document(options: Options, item: PDPCDecisionItem) -> CorpusDocument:
    """
    Gets a CorpusDocument from a PDPCDecisionItem.
    If 'extra_corpus' option is enabled in options, it will return a CorpusDocument
    using experimental versions of CorpusDocumentFactory.

    :param options: Options passed from command line script.
    :param item: The PDPCDecisionItem to get a document from.
    :return: A CorpusDocument.
    """
    from urllib.parse import urlparse
    url = urlparse(item.download_url)
    if url.path[-3:] == 'pdf':
        if options.get('extra_corpus'):
            for factory_class in factory_list:
                if factory_class.check_decision(item, options):
                    return factory_class.from_decision_item(item, options)
        else:
            return BasicCorpusFactory.from_decision_item(item, options)


def create_corpus_file(options: Options, item: PDPCDecisionItem) -> str:
    """
    Writes a corpus file in the folder as specified in options. Checks if there is already an
    existing file in the folder and renames accordingly to prevent overwriting.

    :param options: Options passed from command line script.
    :param item: The PDPCDecisionItem to get a document from.
    :return: The path of the destination file.
    """
    logger.info(f'Now working on: {item}')
    logger.info(f'Source file: {item.download_url}')
    text = get_document(options, item).get_text_as_paragraphs()
    destination_filename = f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent}.txt"
    corpus_folder_ = options["corpus_folder"]
    destination = os.path.join(corpus_folder_, destination_filename)
    if os.path.isfile(
            os.path.join(corpus_folder_, f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} (1).txt")):
        logger.warning('Found secondary format for corpus files. To follow format for this file.')
        file_num = 2
        destination = os.path.join(corpus_folder_,
                                   f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} ({file_num}).txt")
        while os.path.isfile(destination):
            file_num += 1
            destination = os.path.join(corpus_folder_,
                                       f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} ({file_num}).txt")
    if os.path.isfile(destination):
        logger.warning('Found two decisions with the same corpus output file name. Rewriting to secondary format.')
        file_num = 1
        os.rename(destination,
                  os.path.join(corpus_folder_,
                               f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} ({file_num}).txt"))
        file_num += 1
        destination = os.path.join(corpus_folder_,
                                   f"{item.published_date.strftime('%Y-%m-%d')} {item.respondent} ({file_num}).txt")
    with open(destination, 'w') as fOut:
        text = [line + '\n' for line in text]
        fOut.writelines(text)
    logger.info("Wrote: {}".format(destination))
    return destination


def create_corpus(options: Options, items: Sequence[PDPCDecisionItem]) -> None:
    """
    Creates a corpus from a series of PDPCDecisionItem.
    The documents are saved in a folder specified by options["corpus_folder"]
    and is created if it does not exist yet.

    :param options: Options passed from command line script.
    :param items: The PDPCDecisionItem to get a document from.
    :return: None
    """
    logger.info('Now creating corpus.')
    if not os.path.exists(options["corpus_folder"]):
        os.mkdir(options["corpus_folder"])
    for item in items:
        create_corpus_file(options, item)
    logger.info(f'Number of items in corpus: {len(items)}')
    logger.info(f'Finished creating corpus at {options["corpus_folder"]}')
