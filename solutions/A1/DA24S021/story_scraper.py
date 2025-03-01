# Module 3: Scrape Story Details
# story_scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
from config import CONFIG


def download_image(image_url):
    """Download image and return its binary content."""
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        logging.error(f"Failed to download image: {e}")
    return None

def scrape_story_details(top_stories_url):
    """Extract headlines, thumbnails, and URLs from 'Top Stories' page."""
    headers = CONFIG["headers"]
    response = requests.get(top_stories_url, headers=headers)
    
    if response.status_code != 200:
        logging.error(f"Failed to fetch 'Top Stories' page. Status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    stories = []
    scrape_timestamp = datetime.now()
    
    for article in soup.find_all('article'):
        headline = article.find('a', class_=CONFIG["headline_class"])
        img_tag = article.find('img', class_=CONFIG["image_class"])
        link_tag = article.find('a')
        
        if headline and img_tag and link_tag:
            headline_text = headline.text.strip()
            img_src = img_tag.get('src') or img_tag.get('data-src')
            if img_src and urlparse(img_src).scheme == "":
                img_src = urljoin(CONFIG["base_url"], img_src)
            article_url = urljoin(CONFIG["base_url"], link_tag.get('href'))
            image_data = download_image(img_src) if img_src else None
            stories.append({"headline": headline_text, "thumbnail": image_data, "url": article_url, "scrape_timestamp": scrape_timestamp})
    
    logging.info(f"Extracted {len(stories)} stories from 'Top Stories' page.")
    return stories



