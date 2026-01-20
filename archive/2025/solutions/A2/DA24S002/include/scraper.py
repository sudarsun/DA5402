import sys
# from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
import logging
from config import log_file, card_tag, base_html_file

logging.basicConfig(filename=log_file["file_name"], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_dynamic_content(base_url, pause=0.5):
    # Start a session for persistent connections
    session = requests.Session()

    # Make the initial request to get the base page
    response = session.get(base_url)
    response.raise_for_status()  # Ensure the request was successful

    # Parse the initial HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Simulate scrolling by identifying AJAX or API calls
    all_content = soup  # Store initial content
    last_height = len(soup.body.contents)  # Initial "height" based on content length

    while True:
        # Analyze the network traffic in browser dev tools to find the API endpoint for additional content
        # Example: Fetch additional content via an API call (adjust URL and params as needed)
        next_page_url = f"{base_url}?offset={last_height}&limit=20"  # Example pagination logic

        # Make a request to fetch more content
        ajax_response = session.get(next_page_url)
        ajax_response.raise_for_status()

        # Parse the new content
        new_soup = BeautifulSoup(ajax_response.text, 'html.parser')

        # Check if new content is loaded
        new_height = len(new_soup.body.contents)
        if new_height == last_height:
            break  # Stop if no new content is loaded

        # Append new content to all_content
        all_content.body.append(new_soup.body)
        last_height = new_height

        # Pause to mimic scrolling behavior and avoid overwhelming the server
        time.sleep(pause)

    return str(all_content)


def scrape_home_page(search_string, base_url):
    
    try:
        raw_data = requests.get(base_url)
        
        return raw_data.text
    except Exception as e:
        logging.error(f"Error running function : {scrape_home_page.__name__}")
        logging.error(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error(exc_tb.tb_lineno)

def scrape_only_stories(html_text_data, search_string, base_url):
    soup = BeautifulSoup(html_text_data, 'html.parser')
    link = base_url+soup.find(string=search_string).parent.attrs['href'][1:]
    story_list_html = scrape_dynamic_content(link)
    return story_list_html

