# Module 6: Orchestration Script
# orchestrator.py

import logging
from config import CONFIG
from google_news_scraper import scrape_google_news_homepage
from top_stories_scraper import scrape_top_stories
from story_scraper import scrape_story_details
from database_storage import store_in_database
from deduplication import is_duplicate
from database_storage import create_database_if_not_exists

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        filename=CONFIG["log_file"],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

def main():
    setup_logging()
    logging.info("Scraper started.")
    
    homepage_html = scrape_google_news_homepage()
    if not homepage_html:
        logging.error("Failed to scrape homepage.")
        return
    
    top_stories_link = scrape_top_stories(homepage_html, CONFIG["top_stories_identifier"])
    if not top_stories_link:
        logging.error("Failed to find 'Top Stories' link.")
        return
    
    stories = scrape_story_details(top_stories_link)
    if not stories:
        logging.error("Failed to scrape stories.")
        return
    
    create_database_if_not_exists(CONFIG["db_config"])

    unique_stories = 0
    for story in stories:
        if not is_duplicate(story, CONFIG["db_config"], threshold=0.85):
            store_in_database([story], CONFIG["db_config"])
        # if not is_duplicate(story, CONFIG["db_config"]):
        #     store_in_database([story], CONFIG["db_config"])
            unique_stories += 1
    
    logging.info(f"Stored {unique_stories} new stories in the database.")
    
    logging.info("Scraper finished execution.")

if __name__ == "__main__":
    main()
