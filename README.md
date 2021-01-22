# Scrape Art
Scrapers to scrape art images and metadata from Wikiart and Wikimedia Commons. The purpose is to help contribute an art dataset to academia for non-commerical machine learning
research- for example in image captioning, image generation, or image classiifcation. Metadata of art genre, style, title, and art images will allow for a diverse scope 
of machine leanring research  

## How to run 
Download the selenium [ChromeDriver](https://chromedriver.chromium.org/downloads) and move it to the repo's root  
`notebook_wikiart_scraper.ipynb`- Python notebook that carrys out crawling. Notebook format is useful to debug and improve on the crawling    
`python wikiart_scraper.py`- To run the crawler with multiprocessing. Faster to retrieve images and metadata  

## Requirements 
* bs4 (BeautifulSoup)
* urllib
* selenium 
* regex 
* tqdm 
