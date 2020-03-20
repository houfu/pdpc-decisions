#  MIT License Copyright (c) 2020. Houfu Ang

import csv


def save_scrape_results_to_csv(options, scrape_results):
    print('Saving scrape results as a csv file.')
    with open(options["csv_path"], 'w', newline='', encoding='utf-8') as f:
        csvwriter = csv.writer(f)
        if options['extras']:
            csvwriter.writerow(
                ['published_date', 'title', 'respondent', 'summary', 'download_url', 'citation', 'referred_by',
                 'referring_to'])
            for result in scrape_results:
                csvwriter.writerow(
                    [result.published_date, result.title, result.respondent, result.summary, result.download_url,
                     result.citation, result.referred_by, result.referring_to])
        else:
            csvwriter.writerow(['published_date', 'title', 'respondent', 'summary', 'download_url'])
            for result in scrape_results:
                csvwriter.writerow(
                    [result.published_date, result.title, result.respondent, result.summary, result.download_url])
    print('Save completed, files saved at ', options["csv_path"])
