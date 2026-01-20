from pymongo import MongoClient, DESCENDING
import logging
import module1, module4

logger = logging.getLogger(__name__)
config = module1.load_config()
MONGO_URI = f"mongodb://{config['database']['host']}:{config['database']['port']}/"
DATABASE_NAME = f"{config['database']['name']}"

def shorten_string(string, max_length=50):
    """Truncate long strings while preserving hash visibility.
    
    Args:
        string (str): Input string to process
        max_length (int): Maximum length before truncation
        
    Returns:
        str: Truncated string with ellipsis if shortened
    """
    return (string[:max_length] + "...") if len(string) > max_length else string

def find_duplicates():
    """Identify duplicate documents using configured unique field.
    
    Returns:
        list: Groups of duplicate documents with:
            - Common field value
            - Array of document IDs
            - Duplicate count
            
    Raises:
        Exception: Propagates database errors upward
    """
    try:
        with MongoClient(MONGO_URI) as client:
            col = client[DATABASE_NAME]['fs.files']
            
            return list(col.aggregate([
                {"$group": {
                    "_id": f"${config['deduplication']['field']}",
                    "duplicates": {"$push": "$_id"},
                    "count": {"$sum": 1}
                }},
                {"$match": {"count": {"$gt": 1}}}
            ]))
            
    except Exception as e:
        logger.error(f"Duplicate detection failed: {e}")
        raise

def perform_deduplication(duplicate_groups, silent=False):
    """Remove duplicate documents while preserving most recent versions.
    
    Args:
        duplicate_groups (list): Output from find_duplicates()
        silent (bool): Suppress debug logging
        
    Returns:
        bool: True if operation completed successfully
        
    Process:
        1. Skips processing if no duplicates found
        2. For each duplicate group:
           - Keeps newest document by uploadDate
           - Removes older duplicates
           - Deletes associated chunks
    """
    if not duplicate_groups:
        logger.info("No duplicates found in database")
        logger.info(f"Total datapoints in Database: {module4.total_datapoints()}")
        return True

    logger.info(f"Processing {len(duplicate_groups)} duplicate groups")
    target_field = config["deduplication"]["field"]
    deleted_total = 0

    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DATABASE_NAME]
            files_col = db['fs.files']
            chunks_col = db['fs.chunks']

            for group in duplicate_groups:
                # Identify documents to preserve/remove
                latest = files_col.find_one(
                    {target_field: group['_id']},
                    sort=[('uploadDate', DESCENDING)]
                )
                if not latest:
                    continue

                # Execute deletion operations
                to_delete = [oid for oid in group['duplicates'] if oid != latest['_id']]
                if to_delete:
                    files_col.delete_many({"_id": {"$in": to_delete}})
                    chunks_col.delete_many({"files_id": {"$in": to_delete}})
                    
                    deleted_count = len(to_delete)
                    deleted_total += deleted_count
                    logger.info(f"Removed {deleted_count} duplicates for {shorten_string(group['_id'])}")

            # Report final status
            remaining = files_col.count_documents({})
            
        logger.info(f"Removed {deleted_total} total duplicates")
        logger.info(f"Total datapoints in Database: {module4.total_datapoints()}")
        return True

    except Exception as e:
        logger.error(f"Deduplication failed: {e}")
        return False

def main():
    duplicate_groups = find_duplicates()
    return perform_deduplication(duplicate_groups)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    main()
