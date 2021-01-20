# Scrape Art
Scrapers to scrape art images and metadata from Wikiart and Wikimedia Commons. The purpose is to help create an art dataset to academia for non-commerical machine learning
research- for example in image captioning, image generation, or image classiifcation. Metadata of art genre, style, title, and art images will allow for a diverse scope 
of machine leanring research  

## How to run: 
`notebook_wikiart_scraper.ipynb`- Python notebook that carrys out scrapping. Useful to debug and improve on the crawling 
`wikiart_scraper.py`- Implements the crawler with multiprocessing. Faster to scrape images and metadata 

## Requirements: 
* bs4 (BeautifulSoup)
* urllib
* selenium 
* ChromeDriver for selenium
* regex 
* tqdm 
