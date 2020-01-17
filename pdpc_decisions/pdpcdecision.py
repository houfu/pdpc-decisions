#  MIT License Copyright (c) 2019. Houfu Ang

import time

import click

from pdpc_decisions.download_file import download_files, create_corpus
from pdpc_decisions.save_file import save_scrape_results_to_csv
from pdpc_decisions.scraper import scrape
from pdpc_decisions.zeeker import zeeker_main


@click.command()
@click.option('--csv', help='Filename for saving the items gathered by scraper as a csv file.',
              default='scrape_results.csv', type=click.Path(dir_okay=False), show_default=True)
@click.option('--download', help='Destination folder for downloads of all PDF/web pages of PDPC decisions',
              default='download/', type=click.Path(file_okay=False), show_default=True)
@click.option('--corpus', help='Destination folder for PDPC decisions converted to text files', default='corpus/',
              type=click.Path(file_okay=False), show_default=True)
@click.option('--action','sub_action', help="Option that will be passed to an action")
@click.argument('action')
def pdpc_decision(csv, download, corpus, action, sub_action):
    """
    Scripts to scrape all decisions of the Personal Data Protection Commission of Singapore.

    Accepts the following actions.

    "all"       Does all the actions (scraping the website, saving a csv, downloading all files and creating a corpus).

    "corpus"    After downloading all the decisions from the website, converts them into text files.

    "csv"      Save the items gathered by the scraper as a csv file.

    "files"     Downloads all the decisions from the PDPC website into a folder.

    "zeeker"    Construct or updates the zeeker database
    """
    start_time = time.time()
    options = {"csv_path": csv, "download_folder": download, "corpus_folder": corpus, "action": action,
               "sub-action": sub_action}
    scrape_results = scrape()
    if action == 'all':
        save_scrape_results_to_csv(options, scrape_results)
        download_files(options, scrape_results)
        create_corpus(options, scrape_results)
    if action == 'csv':
        save_scrape_results_to_csv(options, scrape_results)
    if action == 'files':
        download_files(options, scrape_results)
    if action == 'corpus':
        create_corpus(options, scrape_results)
    if action == 'zeeker':
        zeeker_main(options, scrape_results)
    diff = time.time() - start_time
    print('Finished. This took {}s.'.format(diff))


if __name__ == '__main__':
    pdpc_decision()
