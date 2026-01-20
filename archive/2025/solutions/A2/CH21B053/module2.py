# scripts/module2.py

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

DEFAULT_CONFIG = {
    'base_url': 'https://news.google.com/',
    'output_link_file_module2': 'data/top_stories_link.txt',
    'output_metadata_file_module2': 'data/module2_metadata.json',
    'max_wait_seconds': '15',
    'top_stories_xpath_module2': "//a[contains(@class, 'aqvwYd') and @id='i11' and contains(text(), 'Top stories')]"
}

def load_config(config_path):
    config = ConfigParser()
    config.read_dict({'DEFAULT': DEFAULT_CONFIG})
    config.read(config_path)
    return config['DEFAULT']

def initialize_driver(config):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(int(config['max_wait_seconds']))
    return driver

def extract_top_stories_link(config):
    driver = initialize_driver(config)
    try:
        driver.get(config['base_url'])
        WebDriverWait(driver, int(config['max_wait_seconds'])).until(
            EC.presence_of_element_located((By.XPATH, config['top_stories_xpath_module2']))
        )
        top_stories_element = driver.find_element(By.XPATH, config['top_stories_xpath_module2'])
        top_stories_link = top_stories_element.get_attribute('href')
        if not top_stories_link:
            raise ValueError("Top Stories link attribute is empty.")
        return top_stories_link
    finally:
        driver.quit()

def run_module2(config_path: str):
    config = load_config(config_path)
    os.makedirs(os.path.dirname(config['output_link_file_module2']), exist_ok=True)
    
    top_stories_url = extract_top_stories_link(config)

    with open(config['output_link_file_module2'], 'w', encoding='utf-8') as f:
        f.write(top_stories_url)
    
    metadata = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'homepage_url': config['base_url'],
        'top_stories_url': top_stories_url,
        'xpath_used': config['top_stories_xpath_module2'],
        'module_version': '2.0'
    }
    with open(config['output_metadata_file_module2'], 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Top Stories link extracted: {top_stories_url}")
    print(f"Metadata saved to {config['output_metadata_file_module2']}")
    print(f"Link output saved to {config['output_link_file_module2']}")
    return metadata
