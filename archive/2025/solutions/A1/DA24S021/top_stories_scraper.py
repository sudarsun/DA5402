# Module 2: Extract 'Top Stories' Link
# top_stories_scraper.py

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from config import CONFIG

def scrape_top_stories(homepage_html, identifier):
    """Extract the 'Top Stories' link from the Google News homepage."""
    soup = BeautifulSoup(homepage_html, 'html.parser')
    
    for link in soup.find_all('a'):
        if identifier.lower() in link.text.lower():
            top_stories_link = link.get('href')
            if top_stories_link:
                top_stories_link = urljoin(CONFIG["url"], top_stories_link)
                logging.info(f"Top Stories link found: {top_stories_link}")
                return top_stories_link
    
    logging.warning("No 'Top Stories' link found.")
    return None