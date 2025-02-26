import os
import logging
from datetime import datetime
import module1, module2, module3, module4, module5

def main():
    """Main news scraping and processing pipeline executor.
    
    Workflow:
    1. Configuration loading
    2. Sequential module execution:
       - Homepage scraping
       - Top stories URL extraction
       - Article collection
       - Database storage
       - Deduplication
    3. Comprehensive error handling with stack traces
    4. File-based logging for cronjob monitoring
    
    Raises:
        Exception: Propagates any fatal errors for external monitoring
    """
    # Initialize logging
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, "..","pipeline.log")
    logging.basicConfig(filename=log_path, 
                        level=logging.INFO, 
                        format="%(levelname)s:%(name)s:%(asctime)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    
    try:
        # Load configurations
        config = module1.load_config()
        logging.info(f"--"*10+" RUNNING PIPELINE "+f"--"*10)
        
        # Module 1: Scrape homepage
        logging.info(f"Starting Module 1")
        homepage_data = module1.scrape_homepage(config, silent=True)
        
        # Module 2: Extract "Top Stories" URL
        logging.info(f"Starting Module 2")
        top_stories_soup = module2.extract_top_stories(homepage_data, config, silent=True)
        
        # Module 3: Scrape thumbnails & headlines (handle lazy loading)
        logging.info(f"Starting Module 3")
        articles = module3.get_articles(top_stories_soup, config, silent=True)
        
        # Module 4: Store in DB
        logging.info(f"Starting Module 4")
        module4.store_articles(articles, silent=True)

        # Module 5: De-duplication check
        logging.info(f"Starting Module 5")
        duplicate_groups = module5.find_duplicates()
        module5.perform_deduplication(duplicate_groups, silent=True)
        
        logging.info(f"Pipeline completed successfully")
        logging.info(f"--"*10+" PIPELINE COMPLETED "+f"--"*10)
        
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}", exc_info=True)
        logging.error(f"--"*10+" PIPELINE FAILED "+f"--"*10)
        raise  # Exit with non-zero code for CronJob

if __name__ == "__main__":
    main()