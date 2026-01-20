# Module 4: Store Data in Database
# database_storage.py

import psycopg2
import logging
from config import CONFIG

import psycopg2
import logging

def create_database_if_not_exists(db_config):
    """Check if the PostgreSQL database exists, create it if it does not."""
    try:
        # Connect to the default 'postgres' database
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"]
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s;", (db_config["dbname"],))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_config["dbname"]}";')
            logging.info(f"Database '{db_config['dbname']}' created successfully.")
        else:
            logging.info(f"Database '{db_config['dbname']}' already exists.")

        

        cursor.close()
        conn.close()



        conn = psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"]
        )
        cursor = conn.cursor()

        # Create tables if they do not exist
        cursor.execute(CONFIG["create_headlines_table"])
        cursor.execute(CONFIG["create_images_table"])

        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Tables checked/created successfully.")

    except Exception as e:
        logging.error(f"Error setting up database/tables: {e}")


    # except Exception as e:
    #     logging.error(f"Error checking/creating database: {e}")



def store_in_database(stories, db_config):
    """Store the extracted stories into a PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"]
        )
        cursor = conn.cursor()
        
        # cursor.execute(CONFIG["create_headlines_table"])
        # cursor.execute(CONFIG["create_images_table"])
        
        # unique_stories = 0
        
        for story in stories:
            cursor.execute("INSERT INTO headlines (headline, url, scrape_timestamp) VALUES (%s, %s, %s) RETURNING id;", 
                           (story["headline"], story["url"], story["scrape_timestamp"]))
            headline_id = cursor.fetchone()[0]
            
            if story["thumbnail"]:
                cursor.execute("INSERT INTO images (headline_id, thumbnail) VALUES (%s, %s);", 
                               (headline_id, story["thumbnail"]))
            # unique_stories += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        # logging.info(f"Stored {unique_stories} new stories in the database.")
    except Exception as e:
        logging.error(f"Database error: {e}")
