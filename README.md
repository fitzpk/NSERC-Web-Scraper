# NSERC-Web-Scraper
Python scripts that utilizes the Selenium library (https://selenium-python.readthedocs.io/) to interact with NSERC research awards database (https://www.nserc-crsng.gc.ca/ase-oro/index_eng.asp) and web scrape selected datasets.

webscraper.py is used to set the filters for NSERC's public database and iterate through each entry to retrieve the detailed information of each research award (i.e. competition year, research area, award amount, installment periods, and more).

cleaner.py is used to further process the webscraped data into an analysis-ready dataset. 
