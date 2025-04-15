import psycopg2
from airflow.hooks.base import BaseHook

def store_data_in_postgres(news_data):
    """Stores scraped news data in PostgreSQL."""
    
    # Retrieve connection details from Airflow
    conn = BaseHook.get_connection("postgress_news")
    db_conn = psycopg2.connect(
        dbname=conn.schema,
        user=conn.login,
        password=conn.password,
        host=conn.host,
        port=conn.port
    )

    cursor = db_conn.cursor()

    # Ensure table exists
    create_table_query = """
        CREATE SCHEMA IF NOT EXISTS news;
        CREATE TABLE IF NOT EXISTS news.news_articles (
            id SERIAL PRIMARY KEY,
            headline TEXT NOT NULL,
            image_url TEXT,
            scrape_timestamp TIMESTAMP DEFAULT NOW(),
            UNIQUE (headline, scrape_timestamp)
        );
    """
    cursor.execute(create_table_query)

    # Insert only valid data
    cleaned_data = [
        (headline, image_url if image_url else None, timestamp)
        for (headline, image_url, timestamp) in news_data
    ]

    if cleaned_data:
        sql = """
            INSERT INTO news.news_articles (headline, image_url, scrape_timestamp)
            VALUES (%s, %s, %s)
            ON CONFLICT (headline, scrape_timestamp) DO NOTHING;
        """
        cursor.executemany(sql, cleaned_data)
        db_conn.commit()
        print(f"✅ Successfully stored {len(cleaned_data)} articles.")
    else:
        print("⚠️ No valid news data found for insertion.")

    cursor.close()
    db_conn.close()
