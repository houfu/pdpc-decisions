#  MIT License Copyright (c) 2020. Houfu Ang

import os

from pdpc_decisions.save_file import save_scrape_results_to_csv


def test_save_scrape_results_to_csv(decisions_extras_gold, decisions_gold, options_test):
    try:
        save_scrape_results_to_csv(options_test, decisions_extras_gold)
        no_extras = options_test.copy()
        no_extras['extras'] = False
        save_scrape_results_to_csv(no_extras, decisions_gold)
    finally:
        os.remove(options_test['csv_path'])
