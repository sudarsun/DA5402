CONFIG = {
    "log_file": "scraper.log",  # Log file path
    "url": "https://news.google.com/",  # Google News homepage URL
    "top_stories_identifier": "Top stories",  # Identifier for 'Top Stories' link
    "base_url": "https://news.google.com",  # Base URL for relative links
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    },
    "headline_class": "gPFEn",  # CSS class for headlines
    "image_class": "Quavad vwBmvb",  # CSS class for images
    "db_config": {
        "dbname": "news_db", # put your database name here
        "user": "postgres",  # put your database username here
        "password": "8881",  # put your database password here
        "host": "localhost",  # put your database host here
        "port": "5432"      # put your database port here
    },
    "create_headlines_table": """
        CREATE TABLE IF NOT EXISTS headlines (
            id SERIAL PRIMARY KEY,
            headline TEXT UNIQUE,
            url TEXT UNIQUE,
            scrape_timestamp TIMESTAMP
        );
    """,
    "create_images_table": """
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            headline_id INTEGER REFERENCES headlines(id) ON DELETE CASCADE,
            thumbnail BYTEA
        );
    """
}
