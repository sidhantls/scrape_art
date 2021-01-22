from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from selenium import webdriver
import os
from pathlib import Path
import time
import regex as re
from itertools import repeat
from multiprocessing import Pool
from tqdm import tqdm


def get_art_urls_from_genre(genre_art_html):
    """
    input: html of genre page that contains all its art titles
    output: list of beautiful soup objects containing all art titles on the page
    """
    genre_soup = BeautifulSoup(genre_art_html, 'html.parser')
    title_blocks = genre_soup.find_all('div', "title-block")
    print(f'\nNumber of art titles {len(title_blocks)}')
    return title_blocks


def go_to_art_page(website_url, title_block):
    """
    input: block soup object containing details of art details
    output: return art bs4 object
    """
    art_address = title_block.find('a', 'artwork-name ng-binding')
    art_url = urljoin(website_url, art_address['href'])
    art_page_html = requests.get(art_url).text

    return art_page_html


def clean_string(string):
    # remove filename illegal chars
    string = re.sub("[?():/]", "", string)

    return string.strip().replace('"', '').lower()


def get_art_details_from_page(art_page_html):
    """
    input: soup object of art page
    output: dictionary of details of art from page
    """
    art_page_soup = BeautifulSoup(art_page_html, 'html.parser')
    # access block that contains art metadata
    art_article = art_page_soup.find_all('article')
    if len(art_article) == 0:
        return {}
    else:
        art_article = art_page_soup.find_all('article')[0]

    art_title_name = art_article.h3.text
    art_author_name = art_article.h5.text

    style_genre_container = art_article.find_all('li', 'dictionary-values')
    art_style = style_genre_container[0]

    # if 'style' not in art_style.s.text.lower():
    #     logger.log(message='style not in object: link {art_style}')

    # art style
    art_style_name = art_style.find('a').text

    # get all images on art page
    image_soups = art_page_soup.find_all('img')

    art_image_url = image_soups[0]['src']

    return {'title': clean_string(art_title_name),
            'artist': clean_string(art_author_name),
            'style': clean_string(art_style_name),
            'image_url': art_image_url}


def get_art_page_url(website_url, title_block):
    """
    input: block soup object containing details of art details
    output: return art bs4 object
    """
    art_address = title_block.find('a', 'artwork-name ng-binding')
    art_url = urljoin(website_url, art_address['href'])

    return art_url


def scroll_down_to_bottom(driver):
    """
    scroll down to load more art
    """
    def load_more(driver):
        time.sleep(2)
        driver.find_element_by_class_name('load-more-phrase').click()

    def close_accidental_zoom(driver):
        time.sleep(2)
        driver.find_element_by_class_name('sueprsized-navigation-close').click()

    for i in range(500):
        try:
            load_more(driver)
        except:
            try:
                close_accidental_zoom(driver)
            except:
                try:
                    load_more(driver)
                except:
                    try:
                        close_accidental_zoom(driver)
                    except:
                        return 0


def parallel_get_art_details(art_url, genre_name, write_folder):
    art_page = requests.get(art_url).text

    art_metadata = get_art_details_from_page(art_page)
    if not art_metadata:
        return

    csv_filepath = write_folder/f'{genre_name}.csv'
    url = art_metadata['image_url']

    response = requests.get(url, stream=True)
    ext = response.headers['content-type'].split('/')[-1]

    write_sub_folder = write_folder/f"{genre_name}"

    if not write_sub_folder.exists():
        write_sub_folder.mkdir()

    if len(art_metadata['title']) >= 150:
        fname = art_metadata['title'][:150] + ('.' + ext)
    else:
        fname = art_metadata['title'] + ('.' + ext)

    image_path = write_sub_folder/fname
    image_path = image_path.relative_to(os.getcwd())

    with open(image_path, 'wb') as f:
        f.write(response.content)

    if not csv_filepath.exists():
        with open(csv_filepath, 'w', encoding="utf-8") as f:
            f.writelines('artist,title,style,image_path\n')
            f.writelines(
                f"{art_metadata['artist']},{art_metadata['title']},{art_metadata['style']},{str(image_path)}\n"
            )
    else:
        with open(csv_filepath, 'a', encoding="utf-8") as f:
            f.writelines(
                f"{art_metadata['artist']},{art_metadata['title']},{art_metadata['style']},{str(image_path)}\n"
            )


if __name__ == '__main__':

    # destination
    write_folder = Path(os.path.join(os.getcwd(), 'crawl_data_parallel'))

    if not write_folder.exists():
        write_folder.mkdir()

    # crawl source
    website_url = 'https://www.wikiart.org/'

    # go to genre page
    website_genre_page = urljoin(website_url, 'en/paintings-by-genre')
    response = requests.get(website_genre_page)
    genre_page_soup = BeautifulSoup(response.text, 'html.parser')

    # get links of each genre
    genres_container = genre_page_soup.find_all('ul', 'dictionaries-list')[0]

    # try out
    genres_container = genre_page_soup.find('ul', 'dictionaries-list')
    genre_link_containers = genres_container.find_all('a')

    driver = webdriver.Chrome()
    driver.minimize_window()

    for genre_link_container in tqdm(genre_link_containers):
        extension = genre_link_container['href']
        genre_name = genre_link_container.text
        genre_name = ''.join(filter(str.isalpha, genre_name))

        genre_url = urljoin(website_url, extension)

        # go to the genre page that contains all its art
        driver.get(genre_url)

        # scroll to bottom
        status = scroll_down_to_bottom(driver)

        genre_art_page = driver.page_source
        art_title_blocks = get_art_urls_from_genre(genre_art_page)

        art_urls = []
        num_repeats = len(art_title_blocks)

        for website_url, title_block in zip(repeat(website_url, num_repeats), art_title_blocks):
            art_urls.append(get_art_page_url(website_url, title_block))

        num_iters = len(art_urls)
        arguments = zip(art_urls,
                        repeat(genre_name, num_iters),
                        repeat(write_folder, num_iters))

        with Pool() as p:
            p.starmap(parallel_get_art_details, arguments)
