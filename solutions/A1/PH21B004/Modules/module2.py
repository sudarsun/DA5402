import module1
import logging

logger = logging.getLogger(__name__)

def extract_top_stories(homepage_data, config, silent=False):
    """Extract and format the Top Stories URL from homepage content.
    
    Args:
        homepage_data (BeautifulSoup): Parsed homepage content
        config (dict): Configuration with scraping parameters
        silent (bool): Disable debug logging when True
        
    Returns:
        str: Soup of the Top Stories link
    
    Note:
        Handles relative URLs by combining with base URL from config
        Uses case-insensitive text matching for link identification
    """
    top_stories_link = None
    
    # Scan all links for configured section name
    for link in homepage_data.find_all("a"):
        link_text = link.get_text(strip=True).lower()
        target_text = config["scraping"]["sub_link_name"].lower()
        
        if target_text in link_text:
            top_stories_link = link.get("href")
            break  # First matching link only

    if top_stories_link:
        # Construct absolute URL from relative path
        base_url = config["scraping"]["base_url"].rstrip('/')
        relative_path = top_stories_link.lstrip('/')
        top_stories_link = f"{base_url}/{relative_path}"
        logger.info(f"Top Stories Link: {top_stories_link}")
        
    else:
        logger.error("Top Stories link not found.")

    soup = module1.scrape_site(top_stories_link)
    # print(f'{len(soup[0]) = }')

    return soup

def main():
    """Main execution flow for standalone operation."""
    config = module1.load_config()
    homepage_data = module1.scrape_homepage(config)
    extract_top_stories(homepage_data, config)

if __name__ == "__main__":
    # Configure console logging for direct execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    main()
