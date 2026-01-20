# scripts/module4.py

import os
import sys
import json
import base64
import requests
from datetime import datetime
from configparser import ConfigParser

import psycopg2
from psycopg2 import sql

DEFAULT_CONFIG = {
    # Database settings
    'db_host_module4': 'postgres',
    'db_port_module4': '5432',
    'db_name_module4': 'airflow',
    'db_user_module4': 'airflow',
    'db_password_module4': 'yourpassword',

    # Table names
    'image_table_module4': 'image_data',
    'meta_table_module4': 'meta_data',

    # Input stories file
    'stories_file_module4': 'data/module3_stories.json',

    # Path for status file
    'status_file_module4': 'dags/run/status'
}

def load_config(config_path):
    config = ConfigParser()
    config.read_dict({'DEFAULT': DEFAULT_CONFIG})
    config.read(config_path)
    return config["DEFAULT"]

def download_image_as_base64(image_url):
    """
    Downloads the image and returns base64-encoded bytes.
    """
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            return base64.b64encode(response.content)
        else:
            print(f"Failed to download image: {image_url}, status={response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
        return None

def insert_story(conn, image_table, meta_table, story):
    """
    Insert one story into meta_data (if not duplicate),
    store base64 image in image_data if new.
    Returns True if inserted, False if duplicate or error.
    """
    try:
        cur = conn.cursor()

        # Insert into meta_data using ON CONFLICT DO NOTHING
        insert_meta = sql.SQL(
            """
            INSERT INTO {table} (headline, article_link, scrape_timestamp)
            VALUES (%s, %s, %s)
            ON CONFLICT ON CONSTRAINT unique_story
            DO NOTHING
            RETURNING id
            """
        ).format(table=sql.Identifier(meta_table))

        cur.execute(insert_meta, (
            story["headline"],
            story["article_link"],
            story["timestamp"]
        ))
        meta_id = cur.fetchone()  # None if duplicate
        if not meta_id:
            conn.rollback()
            cur.close()
            return False  # Duplicate

        meta_id = meta_id[0]

        # Insert base64 image if we have it
        base64_image = download_image_as_base64(story["thumbnail"])
        if base64_image:
            insert_image = sql.SQL(
                "INSERT INTO {table} (meta_id, image_data) VALUES (%s, %s) RETURNING id"
            ).format(table=sql.Identifier(image_table))
            cur.execute(insert_image, (meta_id, psycopg2.Binary(base64_image),))

        conn.commit()
        cur.close()
        return True
    except Exception as error:
        print("Error inserting story:", error)
        conn.rollback()
        return False

def fetch_headline_image_pairs(conn, meta_table, image_table):
    cur = conn.cursor()
    query = sql.SQL(
        """
        SELECT m.headline, encode(i.image_data, 'base64') as base64_image
        FROM {meta_table} m
        JOIN {image_table} i ON m.id = i.meta_id
        """
    ).format(
        meta_table=sql.Identifier(meta_table),
        image_table=sql.Identifier(image_table)
    )
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    return results

def run_module4(config_path: str):
    """
    1. Connect to Postgres
    2. Insert stories from 'stories_file_module4'
    3. Write # of new inserts to 'status_file_module4'
    """
    config = load_config(config_path)

    try:
        conn = psycopg2.connect(
            host=config["db_host_module4"],
            port=config["db_port_module4"],
            database=config["db_name_module4"],
            user=config["db_user_module4"],
            password=config["db_password_module4"]
        )
    except Exception as e:
        print("Database connection failed:", e, file=sys.stderr)
        sys.exit(1)

    # Read stories
    stories_file = config["stories_file_module4"]
    try:
        with open(stories_file, "r", encoding="utf-8") as f:
            stories = json.load(f)
    except Exception as e:
        print("Failed to read stories file:", e, file=sys.stderr)
        conn.close()
        sys.exit(1)

    image_table = config["image_table_module4"]
    meta_table = config["meta_table_module4"]

    inserted_count = 0
    for story in stories:
        if insert_story(conn, image_table, meta_table, story):
            inserted_count += 1

    conn.close()
    print(f"Inserted {inserted_count} new stories out of {len(stories)} total.")

    # Write status file
    status_file = config["status_file_module4"]
    os.makedirs(os.path.dirname(status_file), exist_ok=True)
    with open(status_file, "w", encoding="utf-8") as f:
        f.write(str(inserted_count))

    return inserted_count
