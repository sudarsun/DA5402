from pymongo import MongoClient
from gridfs import GridFS
import hashlib
import logging
import requests
import module1, module3

logger = logging.getLogger(__name__)
config = module1.load_config()
MONGO_URI = f"mongodb://{config['database']['host']}:{config['database']['port']}/"
DATABASE_NAME = f"{config['database']['name']}"

def hash_binary_data(data):
    """Generate SHA-256 hash for binary data.
    
    Args:
        data (bytes): Input data to hash
        
    Returns:
        str: Hexadecimal string representation of the hash
    """
    return hashlib.sha256(data).hexdigest()

def total_datapoints():
    with MongoClient(MONGO_URI) as client:
        return len(list(client[DATABASE_NAME]['fs.files'].find()))

def is_file_present(img_hl_hash):
    """Check for existing GridFS file using composite image-headline hash.
    
    Args:
        img_hl_hash (str): Combined hash of image and headline
        
    Returns:
        bool: True if matching file exists, False otherwise
    """
    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DATABASE_NAME]
            return bool(db.fs.files.find_one(
                {"metadata.img_hl_hash": img_hl_hash}
            ))
    except Exception as e:
        logger.error(f"Database check error: {e}")
        return False

def download_and_store_image(image_url, metadata, silent=False, check_exists=True):
    """Store image in GridFS with metadata after duplicate check.
    
    Args:
        image_url (str): URL of image to store
        metadata (dict): Article metadata including headline
        silent (bool): Disable debug logging/printing
        check_exists (bool): Enable duplicate checking
        
    Returns:
        bool: True if stored successfully, False otherwise
    """
    try:
        response = requests.get(image_url, stream=True)
        if not response.ok:
            logger.debug(f"Image download failed: HTTP {response.status_code}")
            return False

        img_hash = hash_binary_data(response.content)
        hl_hash = hash_binary_data(metadata['headline'].encode())
        composite_hash = img_hash + hl_hash
        metadata['img_hl_hash'] = composite_hash

        if check_exists and is_file_present(composite_hash):
            if not silent:
                print("Duplicate detected - skipping upload")
            return False

        with MongoClient(MONGO_URI) as client:
            fs = GridFS(client[DATABASE_NAME])
            file_id = fs.put(
                response.content,
                filename=image_url.split("/")[-1],
                metadata=metadata
            )
            
        if not silent:
            print(f"Stored image with ID: {file_id}")
        return True

    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        return False

def store_articles(articles, silent=False, check_exists=True):
    """Batch store article thumbnails with metadata.
    
    Args:
        articles (list): Articles with thumbnail URLs and metadata
        silent (bool): Suppress debug logging
        check_exists (bool): Enable duplicate prevention
        
    Returns:
        bool: True if all stored successfully, False otherwise
    """
    success_count = 0
    try:
        for idx, article in enumerate(articles, 1):
            if not silent:
                print(f"Processing article {idx}/{len(articles)}")
                print(f"Headline: {article['headline']}")

            if download_and_store_image(
                article['thumbnail'], 
                article, 
                silent, 
                check_exists
            ):
                success_count += 1

            if not silent:
                print("--"*50)

        success_rate = success_count/len(articles)
        if success_rate == 1:
            logger.info(f"Successfully stored all {success_count} articles")
        else:
            logger.warning(f"Stored only {success_count}/{len(articles)} articles due to duplicates")


        logger.info(f"Total datapoints in Database: {total_datapoints()}")

        return success_count == len(articles)
        
    except Exception as e:
        logger.error(f"Article storage failed: {e}")
        return False

def main():
    """Main execution flow for standalone operation."""
    config = module1.load_config()
    articles = module3.get_articles(
        module1.scrape_site(config["skipper"]["top_stories_link_uk"]), 
        config
    )
    return store_articles(articles, check_exists=True)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    main()
