#!/usr/bin/env python3
import argparse
import logging
import time
from datetime import datetime
from module1 import scrape_page
from module2 import scrape_top_stories_link 
from module3 import setup_driver,scrape_top_stories_page
from module4 import get_mongo_database
from module5 import insert_data, scrape_google_news
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("orchestrator.log"),
            logging.StreamHandler()
        ]
    )
def orchestrate_pipeline(args):
    logging.info("Pipeline execution started.")
    overall_start = datetime.now()
    # Module 1: Scrape the home page.
    logging.info("Module 1: Scraping the home page.")
    homepage_file = args.output_file
    scrape_page(args.home_url, args.chromedriver, homepage_file)
    logging.info(f"Module 1: Home page source saved to {homepage_file}.")
    # Module 2: Extract the Top Stories link.
    logging.info("Module 2: Extracting Top Stories link from the home page.")
    top_stories_url = scrape_top_stories_link(args.home_url, args.top_stories_text, args.chromedriver)
    if not top_stories_url:
        logging.error("Module 2: Top Stories link not found. Aborting pipeline.")
        return
    logging.info(f"Module 2: Top Stories link found: {top_stories_url}")
    # Module 3: Extract headlines and thumbnails from the Top Stories page.
    logging.info("Module 3: Extracting article data from Top Stories page.")
    driver = setup_driver(args.chromedriver)
    driver.get(top_stories_url)
    articles_data = scrape_top_stories_page(driver)
    if not articles_data:
        logging.error("Module 3: No article data extracted. Aborting pipeline.")
        return
    logging.info(f"Module 3: Extracted articles.")
    # Module 4 and 5: Store the extracted data in the database and check duplicates.
    if not top_stories_url:
        logging.error("Top Stories link not found. Aborting Step 2.")
    else:
        driver = setup_driver(args.chromedriver)
        logging.info(f"Using Top Stories link: {top_stories_url}")
        scrape_google_news(top_stories_url, driver)

    overall_end = datetime.now()
    duration = overall_end - overall_start
    logging.info(f"Pipeline execution completed in {duration}.")
def main():
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Orchestrate the cascaded news scraping pipeline. "
                    "Each module’s output is passed as input to the next."
    )
    parser.add_argument(
        "--home_url",
        type=str,
        default="https://news.google.com",
        help="Home page URL (default: https://news.google.com)"
    )
    parser.add_argument(
        "--top_stories_text",
        type=str,
        default="top stories",
        help="Text to search for the Top Stories link (e.g., 'top stories')"
    )
    parser.add_argument(
        "--chromedriver",
        type=str,
        default=r"C:\Users\SUKRITI\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe",
        help="Path to the chromedriver executable."
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="homepage.html",
        help="File to save the scraped home page HTML (default: homepage.html)"
    )
    args = parser.parse_args()

    logging.info("Orchestrator script invoked.")
    orchestrate_pipeline(args)
    logging.info("Orchestrator script finished.")

if __name__ == "__main__":
    main()
