#  MIT License Copyright (c) 2020. Houfu Ang

import logging
import os
import time

import click

from pdpc_decisions.classes import Options
from pdpc_decisions.corpus_text import create_corpus
from pdpc_decisions.download_file import download_files
from pdpc_decisions.save_file import save_scrape_results_to_csv
from pdpc_decisions.scraper import Scraper
from pdpc_decisions.scraper_extras import scraper_extras

logger = logging.getLogger(__name__)


@click.command()
@click.option('--csv', help='Filename for saving the items gathered by scraper as a csv file.',
              default='scrape_results.csv', type=click.Path(dir_okay=False), show_default=True)
@click.option('--download', help='Destination folder for downloads of all PDF/web pages of PDPC decisions',
              default='download/', type=click.Path(file_okay=False), show_default=True)
@click.option('--corpus', help='Destination folder for PDPC decisions converted to text files', default='corpus/',
              type=click.Path(file_okay=False), show_default=True)
@click.option('--root', '-r', help='Root directory for downloads and files', type=click.Path(file_okay=False),
              default=os.getcwd(), show_default=True)
@click.option('--extras/--no-extras', default=False, help='Add extra features to the data scraped', show_default=True)
@click.option('--extra-corpus/--no-extra-corpus', default=False, help='Enable experimental features for corpus',
              show_default=True)
@click.option('--verbose', '-v', default=False, help='Verbose output', show_default=True, is_flag=True)
@click.argument('action')
def pdpc_decision(csv, download, corpus, action, root, extras, extra_corpus, verbose):
    """
    Scripts to scrape all decisions of the Personal Data Protection Commission of Singapore.

    Accepts the following actions.

    "all"       Does all the actions (scraping the website, saving a csv, downloading all files and creating a corpus).

    "corpus"    After downloading all the decisions from the website, converts them into text files.

    "csv"      Save the items gathered by the scraper as a csv file.

    "files"     Downloads all the decisions from the PDPC website into a folder.
    """
    start_time = time.time()
    if verbose:
        logging.basicConfig(level='INFO')
    options = Options(csv_path=csv, download_folder=download, corpus_folder=corpus, action=action, root=root,
                      extras=extras, extra_corpus=extra_corpus)
    logger.info(f'Options: {options}')
    if options['root']:
        os.chdir(root)
    scrape_results = Scraper.scrape()
    if (action == 'all') or (action == 'files'):
        download_files(options, scrape_results)
    if (action == 'all') or (action == 'corpus'):
        create_corpus(options, scrape_results)
    if extras and ((action == 'all') or (action == 'csv')):
        scraper_extras(scrape_results)
    if (action == 'all') or (action == 'csv'):
        save_scrape_results_to_csv(options, scrape_results)
    diff = time.time() - start_time
    logger.info('Finished. This took {}s.'.format(diff))


if __name__ == '__main__':
    pdpc_decision()
