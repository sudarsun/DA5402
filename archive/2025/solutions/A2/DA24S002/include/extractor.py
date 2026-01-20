import sys

from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime
from config import path_config, log_file, date_format, card_tag, base_url_and_search_string
import logging
from io import BytesIO
import base64


logging.basicConfig(filename=log_file["file_name"], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# IMAGE_PATH = path_config["image_path"]+"\\"

# if (not os.path.exists(os.getcwd()+"\\"+path_config["image_path"])):
#     os.makedirs(os.getcwd()+"\\"+path_config["image_path"])

def extract_article_url(story, baseUrl):
    return baseUrl + [v for v in story.find_all('a')][1].attrs['href'][1:]

def extract_article_date(story):
    date_object = datetime.now()
    date_string = ""
    try:
        
        parent = [v for v in story.find_all('a')][1].parent
        if (parent.find('time')):
            date_string = parent.find('time').attrs['datetime']
            date_object = datetime.strptime(date_string, date_format)
        else:
            # print([v for v in story.find_all('a')][1].text)
            while(not parent.find('time')):
                parent = parent.parent
            date_string = parent.find('time').attrs['datetime']
            date_object = datetime.strptime(date_string, date_format)

    except:

        # print([v for v in story.find_all('a')][1].text)
        # print([v for v in story.find_all('a')][1].parent)
        # print("Not able to extract article time, so saving current time instead")
        logging.error(f"Error running function : {extract_article_date.__name__}")

    return [date_object, date_string]

def extract_story_data_list(story_list_html):
    soup = BeautifulSoup(story_list_html, 'html.parser')
    cards = [v1 for v1 in [v for v in soup.find('main').find(card_tag).children][1].find_all(card_tag)][::2]

    story_data_list = []
    
    for index, card in enumerate(cards):
        headline, image, imageUrl, articleUrl, articleDate = extract_story_data(card, index)
        if headline != "":
            story_data_list.append({
                "headline": headline,
                "image": image,
                "imageUrl": imageUrl,
                "articleUrl": articleUrl,
                "articleDate": articleDate
            })

    return story_data_list




def extract_story_data(card, index):
    image_found = False
    image_data = ""
    headline = ""
    imageUrl = ""
    articleUrl = ""
    articleDate = ""

    for image in card.find_all('img'):
        try:
            imageUrl = image.attrs['src']
            imgDataResponse = requests.get(base_url_and_search_string['base_url']+imageUrl)

            image_data = BytesIO(imgDataResponse.content).getvalue()   

            if imgDataResponse.status_code == 200:
                image_found = True
                break
        except Exception as error:
            # print(error)
            continue
    if (not image_found):
        logging.error(f"Error recieving image in function: {extract_story_data.__name__}")
        return [headline, image_data, imageUrl, articleUrl, articleDate]
    headline = [v for v in card.find_all('a')][1].text
    articleUrl = extract_article_url(card, base_url_and_search_string['base_url'])
    [articleDate, articleDateString] = extract_article_date(card)
    image_data = base64.b64encode(image_data).decode('utf-8')

    return [headline, image_data, imageUrl, articleUrl, articleDateString]

