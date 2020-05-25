#  MIT License Copyright (c) 2020. Houfu Ang

import csv
import logging
from typing import List

from pdpc_decisions.classes import Options, PDPCDecisionItem

logger = logging.getLogger(__name__)


def save_scrape_results_to_csv(options: Options, scrape_results: List[PDPCDecisionItem]) -> None:
    logger.info('Saving scrape results as a csv file.')
    with open(options["csv_path"], 'w', newline='', encoding='utf-8') as f:
        csvwriter = csv.writer(f)
        if options['extras']:
            csvwriter.writerow(
                ['published_date', 'title', 'respondent', 'summary',
                 'download_url', 'citation', 'case_number',
                 'referred_by', 'referring_to', 'enforcement'])
            for result in scrape_results:
                if not hasattr(result, 'citation'):
                    result.citation = ''
                if not hasattr(result, 'case_number'):
                    result.case_number = ''
                if not hasattr(result, 'referring_to'):
                    result.referring_to = ''
                if not hasattr(result, 'referred_by'):
                    result.referred_by = ''
                if not hasattr(result, 'enforcement'):
                    result.enforcement = ''
                csvwriter.writerow(
                    [result.published_date, result.title, result.respondent, result.summary,
                     result.download_url, result.citation, result.case_number,
                     result.referred_by, result.referring_to, result.enforcement])
        else:
            csvwriter.writerow(['published_date', 'title', 'respondent', 'summary', 'download_url'])
            for result in scrape_results:
                csvwriter.writerow(
                    [result.published_date, result.title, result.respondent, result.summary, result.download_url])
    logger.info(f'Save completed, files saved at {options["csv_path"]}')
