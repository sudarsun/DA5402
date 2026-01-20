# scripts/module3.py

import os
import sys
import json
import time
from datetime import datetime, timezone
from urllib.parse import urljoin
from configparser import ConfigParser

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

DEFAULT_CONFIG = {
    # Distinct keys for Module 3
    'top_stories_link_file_module3': 'data/top_stories_link.txt',
    'top_stories_page_url_module3': 'https://news.google.com/',
    'output_metadata_file_module3': 'data/module3_metadata.json',
    'output_stories_file_module3': 'data/module3_stories.json',

    # Shared or distinct
    'max_wait_seconds': '15',

    # Distinct keys for scrolling & selectors
    'scroll_pause_module3': '1',
    'scroll_attempts_module3': '5',
    'story_container_selector_module3': 'article',
    'headline_selector_module3': 'a.DY5T1d',
    'thumbnail_selector_module3': 'img'
}

def load_config(config_path):
    config = ConfigParser()
    # Keep case sensitivity in config keys
    config.optionxform = str
    config.read_dict({'DEFAULT': DEFAULT_CONFIG})
    config.read(config_path)

    # Manually fix % encoding issues
    config_dict = {key: value.replace("%", "%%") for key, value in config["DEFAULT"].items()}
    return config_dict

def get_top_stories_url(config):
    """
    Retrieve the Top Stories URL from a file created by Module 2 (or fallback).
    """
    file_path = config["top_stories_link_file_module3"]
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                url = f.read().strip()
                if url:
                    return url
        except Exception as e:
            print(f"Warning: Could not read top stories link file: {e}")
    # Fallback
    return config["top_stories_page_url_module3"]

def initialize_driver(config):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(int(config["max_wait_seconds"]))
    return driver

def scroll_page(driver, pause_time, attempts):
    for _ in range(attempts):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)

def extract_stories(config, html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    stories = []

    print("Parsing HTML content...")

    container_selector = config["story_container_selector_module3"]
    headline_selector = config["headline_selector_module3"]
    # If you want to keep your 'thumbnail_selector_module3', adapt accordingly
    # In your code, you used a figure-based approach. We'll keep that for clarity:
    # For a simpler approach, you can just do: thumbnail_selector = config["thumbnail_selector_module3"]
    # But let's keep your direct approach for a figure-based selector:

    containers = soup.select(container_selector)
    print(f"Found {len(containers)} story containers")

    for container in containers:
        headline_elem = container.select_one(headline_selector)
        # Hard-coded figure approach from your example:
        img_tag = container.select_one("figure.K0q4G img")

        if headline_elem and img_tag:
            headline_text = headline_elem.get_text(strip=True)
            article_link = headline_elem.get('href', '')
            if article_link:
                article_link = urljoin(config["top_stories_page_url_module3"], article_link)

            thumbnail_url = img_tag["src"] if img_tag else None
            if thumbnail_url and thumbnail_url.startswith('/api/attachments/'):
                thumbnail_url = "https://news.google.com" + thumbnail_url

            if headline_text and thumbnail_url:
                stories.append({
                    "headline": headline_text,
                    "article_link": article_link,
                    "thumbnail": thumbnail_url,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                print(f"Extracted story: {headline_text[:50]}...")

    print(f"Extracted {len(stories)} stories.")
    return stories

def run_module3(config_path: str):
    """
    Main entry point for Module 3.
    - Reads config
    - Gets top stories URL from file or fallback
    - Scrolls & extracts headlines + thumbnails
    - Saves to JSON
    - Writes metadata
    """
    config = load_config(config_path)

    top_stories_url = get_top_stories_url(config)
    print(f"Using Top Stories URL: {top_stories_url}")

    driver = initialize_driver(config)
    try:
        driver.get(top_stories_url)
        WebDriverWait(driver, int(config["max_wait_seconds"])).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Scroll
        scroll_page(driver, float(config["scroll_pause_module3"]), int(config["scroll_attempts_module3"]))
        html_content = driver.page_source
    finally:
        driver.quit()

    stories = extract_stories(config, html_content)

    # Save stories
    output_stories = config["output_stories_file_module3"]
    os.makedirs(os.path.dirname(output_stories), exist_ok=True)
    with open(output_stories, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2)

    # Metadata
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "top_stories_page_url": top_stories_url,
        "stories_extracted": len(stories),
        "module_version": "3.0"
    }
    output_meta = config["output_metadata_file_module3"]
    os.makedirs(os.path.dirname(output_meta), exist_ok=True)
    with open(output_meta, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Extracted {len(stories)} stories.")
    print(f"Stories saved to {output_stories}")
    print(f"Metadata saved to {output_meta}")
    return metadata
