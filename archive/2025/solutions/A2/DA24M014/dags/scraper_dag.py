import os
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.models import Variable

# Default Arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG Definition
dag = DAG(
    'news_scraper',
    default_args=default_args,
    description='Scrapes Google News and stores data in Postgres',
    schedule_interval='@hourly',
    catchup=False,
)

# PostgreSQL Table Setup
table_setup = PostgresOperator(
    task_id='setup_postgres_tables',
    postgres_conn_id='postgress_news',
    sql='''
    CREATE TABLE IF NOT EXISTS news.news_articles (
            id SERIAL PRIMARY KEY,
            headline TEXT NOT NULL,
            image_url TEXT,
            scrape_timestamp TIMESTAMP DEFAULT NOW(),
            UNIQUE (headline, scrape_timestamp)
    );
    ''',
    dag=dag,
)

# Scrape Data Task
def scrape_and_store(**kwargs):
    from scripts.scrap import scrape_top_stories  # ✅ Import inside function
    ti = kwargs['ti']
    news_data = scrape_top_stories()
    
    if news_data:
        logging.info(f"✅ Scraped {len(news_data)} articles.")
        ti.xcom_push(key='news_data', value=news_data)
    else:
        logging.warning("⚠️ No news data scraped.")

# Store Data Task
def store_data_task(**kwargs):
    from scripts.dbload import store_data_in_postgres
    ti = kwargs['ti']
    news_data = ti.xcom_pull(task_ids='scrape_top_stories', key='news_data')

    if not news_data:
        logging.warning("⚠️ No news data received for storing.")
        return

    logging.info(f"✅ Storing {len(news_data)} articles.")
    store_data_in_postgres(news_data)

# Create status file to trigger the email DAG
def create_status_file(**kwargs):
    ti = kwargs['ti']
    news_data = ti.xcom_pull(task_ids='scrape_top_stories', key='news_data')
    new_entries = len(news_data) if news_data else 0

    status_path = Variable.get("status_file_path", "/opt/airflow/dags/run/status")
    
    os.makedirs(os.path.dirname(status_path), exist_ok=True)
    with open(status_path, 'w') as f:
        f.write(str(new_entries))
    
    logging.info(f"✅ Status file updated: {new_entries} new articles stored.")

# Define Tasks
scrape_task = PythonOperator(
    task_id='scrape_top_stories',
    python_callable=scrape_and_store,
    dag=dag,
)

store_task = PythonOperator(
    task_id='store_data_in_postgres',
    python_callable=store_data_task,
    dag=dag,
)

status_task = PythonOperator(
    task_id='create_status_file',
    python_callable=create_status_file,
    dag=dag,
)

trigger_email_dag = TriggerDagRunOperator(
    task_id="trigger_send_email_dag",
    trigger_dag_id="send_email_dag",
    wait_for_completion=False,
    dag=dag,
)

# Define Workflow
table_setup >> scrape_task >> store_task >> status_task >> trigger_email_dag
