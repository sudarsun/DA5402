from datetime import datetime
import module1
import logging

logger = logging.getLogger(__name__)

def extract_data_from_articles(articles_soup, config):
    """Extract structured article data from parsed HTML content.
    
    Args:
        articles_soup (ResultSet): Collection of BeautifulSoup article elements
        config (dict): Configuration with CSS class identifiers
        
    Returns:
        list: Cleaned articles with metadata including:
            - Headline text
            - Thumbnail URL
            - Publisher information
            - Publication timestamp
            - Article URL
            - Scrape timestamp
    
    Note:
        Skips incomplete articles missing required fields
        Converts relative URLs to absolute paths
    """
    articles = []
    
    for article in articles_soup[:]:  # Iterate over copy for safe modification
        # Extract core elements using configured CSS classes
        headline = article.find('a', {"class": config['scraping_classes']['hl_class']})
        thumbnail = article.find("img", {"class": config['scraping_classes']['thumbnail_class']})
        url = article.find("a", {"href": True, "class": config['scraping_classes']['url_class']})
        publish_time = article.find("time", {"class": config['scraping_classes']['publish_time_class']})
        publisher = article.find("div", {"class": config['scraping_classes']['publisher_class']})

        # Validate required fields
        if not all([headline, thumbnail, url, publish_time, publisher]):
            continue

        articles.append({
            "headline": headline.get_text(strip=True),
            "thumbnail": f"https://news.google.com{thumbnail['src']}",
            "publisher": publisher.get_text(strip=True),
            "publish_time": publish_time['datetime'],
            "article_url": f"https://news.google.com{url['href']}",
            "scrape_datetime": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        })

    return articles

def get_articles(top_stories_soup, config, silent=False):
    """Execute full article scraping workflow.
    
    Args:
        top_stories_soup (str): Parsed HTML of Top Stories link
        config (dict): Configuration parameters
        silent (bool): Disable debug logging when True
        
    Returns:
        list: Structured article data or empty list on failure
    """
    articles_soup = top_stories_soup.find_all("article")
    articles = extract_data_from_articles(articles_soup, config)
    
    if articles:
        logger.info(f"Successfully scraped {len(articles)} articles.")
    else:
        logger.error("Failed to scrape articles.")

    return articles

def main():
    """Execute main scraping pipeline."""
    config = module1.load_config()
    top_stories_soup = module1.scrape_site(config["skipper"]["top_stories_link_uk"])
    return get_articles(top_stories_soup, config)

if __name__ == "__main__":
    # Configure console logging for direct execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    main()
