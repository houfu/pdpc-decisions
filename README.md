# pdpc-decisions
This package contains utilities which allow you to create a corpus of decisions from the 
Personal Data Protection Commission of Singapore's 
[Data Protection Enforcement Cases](https://www.pdpc.gov.sg/Commissions-Decisions/Data-Protection-Enforcement-Cases).

The primary use of such a corpus is for studying, possibly using data science tools such as 
natural language processing.

It currently has the following features:

* Visit the Personal Data Protection Commission of Singapore's 
[Data Protection Enforcement Cases](https://www.pdpc.gov.sg/Commissions-Decisions/Data-Protection-Enforcement-Cases)
and compile a table of decisions with information from the summaries provided by the PDPC for each case.
* Save this table of decisions as CSV
* Download all the PDF files of the decisions from the PDPC's website. 
If the decision is not a PDF, collects the information provided on the decision web page and saves it as a text file.
* Convert the PDF files into text files

## Requirements
* Python 3
* PDF Miner
* Selenium

## Usage

I have not got round to finalising an install to the command line.

Your best bet is to run the python scripts using the entry point `pdpcdecision.py`

The script accepts the following actions and options:

Accepts the following actions.

  "`all`"       Does all the actions (scraping the website, saving a csv,
  downloading all files and creating a corpus).

  "`corpus`"    After downloading all the decisions from the website, converts
  them into text files.

  "`csv`"      Save the items gathered by the scraper as a csv file.

  "`files`"     Downloads all the decisions from the PDPC website into a
  folder.

Options:
  
  `--csv FILE`            Filename for saving the items gathered by scraper as a
                        csv file.  [default: scrape_results.csv]
  
  `--download DIRECTORY`  Destination folder for downloads of all PDF/web pages
                        of PDPC decisions  [default: download/]
  
  `--corpus DIRECTORY`    Destination folder for PDPC decisions converted to
                        text files  [default: corpus/]
  
  `--help`                Show this message and exit.

## Contact

Feel free to let me have your suggestions, comments or issues using the issue tracker or by 
[emailing me](mailto:houfu@outlook.sg).

It would also be nice to hear how you have used this corpus by using the above contacts. 