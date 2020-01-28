from pdpc_decisions.save_file import save_scrape_results_to_csv
import os


def test_save_scrape_results_to_csv(decisions_gold, options_test):
    try:
        save_scrape_results_to_csv(options_test, decisions_gold)
    finally:
        os.remove(options_test['csv_path'])