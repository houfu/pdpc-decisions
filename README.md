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

## What pdpc-decisions uses
* Python 3
* PDF Miner
* Selenium
* Chrome

## Installation

### Local install
* Clone this repository.

```shell script
git clone https://github.com/houfu/pdpc-decisions.git
```

* Install using `setup.py` (which will also install all dependencies. Except Chrome and ChromeDriver)
```shell script
# cd pdpc-decisions
# pip install .
```

* If necessary, install [Chrome](https://www.google.com/chrome/) 
and [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) for Selenium to work.

The main entry point for the script is `pdpcdecision.py`

### Docker Image

I also dockerised the application for my personal ease of use. 
Basically pull the image from [docker hub](https://hub.docker.com/r/houfu/pdpc-decisions).
```shell script
docker pull houfu/pdpc-decisions
```

After that you can run the image and pass commands and arguments to it.
For example, if you would like the application to do all actions.

```shell script
docker run houfu/pdpc-decisions all
```

This might not be very clever because downloads will be stored in the docker image 
and not easily accessed. You could attach a volume but I have not tried it. 
You should set the option to your volume.

## Usage

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