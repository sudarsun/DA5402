# Module 1: Scrape Google News Homepage
# google_news_scraper.py

import requests
from bs4 import BeautifulSoup
import logging
from config import CONFIG

def scrape_google_news_homepage():
    """Scrape Google News homepage and return HTML content."""
    url = CONFIG["url"]
    headers = CONFIG["headers"]
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info("Successfully scraped Google News homepage.")
            return response.text
        else:
            logging.error(f"Failed to fetch Google News homepage. Status code: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error scraping Google News homepage: {e}")
        return None