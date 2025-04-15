# scripts/module1.py

import os
import sys
import json
from datetime import datetime, timezone
from configparser import ConfigParser

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

DEFAULT_CONFIG = {
    'base_url': 'https://news.google.com/',
    'output_metadata_file': 'data/module1_metadata.json',
    'max_wait_seconds': '15'
}

def load_config(config_path):
    """
    Load configurations from a file with a fallback to default values.
    """
    config = ConfigParser()
    config.read_dict({'DEFAULT': DEFAULT_CONFIG})
    config.read(config_path)
    return config['DEFAULT']

def initialize_driver(config):
    """
    Initialize a headless Selenium WebDriver.
    """
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(int(config['max_wait_seconds']))
    return driver

def access_homepage(config):
    """
    Load the Google News homepage and return minimal metadata.
    """
    driver = initialize_driver(config)
    try:
        driver.get(config['base_url'])
        WebDriverWait(driver, int(config['max_wait_seconds'])).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        page_title = soup.title.string.strip() if soup.title and soup.title.string else "No Title Found"

        metadata = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'homepage_url': config['base_url'],
            'page_title': page_title,
            'module_version': '1.3'
        }
        return metadata
    except Exception as e:
        print(f"Module 1 failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.quit()

def run_module1(config_path: str):
    """
    Main entry point for Module 1. 
    - Loads config from config_path
    - Accesses the Google News homepage
    - Saves metadata to JSON
    """
    config = load_config(config_path)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(config['output_metadata_file']), exist_ok=True)

    # Access homepage and get metadata
    metadata = access_homepage(config)

    # Save metadata
    with open(config['output_metadata_file'], 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print("Homepage accessed successfully.")
    print(f"Metadata saved to {config['output_metadata_file']}")
    return metadata  # Optionally return metadata for logging or XCom in Airflow
