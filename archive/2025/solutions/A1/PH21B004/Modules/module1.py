import time
import os
import logging
import yaml
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)
os.environ['WDM_LOG'] = str(logging.NOTSET)  # Suppress webdriver-manager logs


def load_config():
    """Load and merge configuration from multiple sources.
    
    Combines environment variables (.env) with YAML configuration (config.yaml).
    Returns a structured configuration dictionary with:
    - Database connection parameters
    - Web scraping settings
    - Deduplication rules
    - Debug mode flag
    
    Returns:
        dict: Unified configuration with environment and file settings
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'Config files')

    load_dotenv(os.path.join(config_path, ".env"))
    
    with open(os.path.join(config_path, "config.yaml"), "r") as f:
        yaml_config = yaml.safe_load(f)

    return {
        "database": {
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "name": os.getenv("DB_NAME")
        },
        "scraping": yaml_config["scraping"],
        "scraping_classes": yaml_config["scraping_classes"],
        "skipper": yaml_config["skipper"],
        "deduplication": yaml_config["deduplication"],
        "debug": os.getenv("DEBUG_MODE", "False").lower() == "true"
    }


def scrape_site(url):
    """Execute full-site JavaScript rendering and content extraction.
    
    Args:
        url (str): Target website URL to scrape
        
    Returns:
        BeautifulSoup: Parsed page content after full dynamic loading
    
    Note:
        Uses headless Chrome browser with automatic driver management
        Implements scroll-based lazy loading activation
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get(url)
        time.sleep(3)  # Initial page load buffer

        # Scroll to bottom until no new content loads
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Content loading buffer
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()


def scrape_homepage(config, silent=False):
    """Execute homepage scraping using configured parameters.
    
    Args:
        config (dict): Loaded configuration dictionary
        silent (bool): Disable debug logging when True
        
    Returns:
        BeautifulSoup: Parsed homepage content or None on failure
    """
    homepage_data = scrape_site(config['scraping']['scraping_url'])
    
    if homepage_data:
        logger.info("Successfully parsed the page.")
    else:
        logger.error("Failed to parse the page.")

    return homepage_data


def main():
    config = load_config()
    scrape_homepage(config)


if __name__ == "__main__":
    # Console-friendly logging format for direct execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    main()
