"""
Airflow DAG that:
1. Runs Module 1 (PythonOperator)
2. Runs Module 2 (PythonOperator)
3. Runs Module 3 (PythonOperator)
4. Creates tables with PostgresOperator
5. Inserts stories + writes status file with PythonOperator (Module 4)
"""

import sys
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Add scripts folder to PYTHONPATH
sys.path.append("/opt/airflow/scripts")

# Import your modules
from module1 import run_module1
from module2 import run_module2
from module3 import run_module3
from module4 import run_module4

DEFAULT_CONFIG_PATH = "/opt/airflow/config/pipeline_config.ini"

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# SQL for creating tables
create_tables_sql = """
CREATE TABLE IF NOT EXISTS meta_data (
    id SERIAL PRIMARY KEY,
    headline TEXT NOT NULL,
    article_link TEXT,
    scrape_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_story UNIQUE (headline)
);

CREATE TABLE IF NOT EXISTS image_data (
    id SERIAL PRIMARY KEY,
    meta_id INT NOT NULL,  -- Foreign key
    image_data BYTEA NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_meta FOREIGN KEY (meta_id) REFERENCES meta_data(id)
);
"""

with DAG(
    dag_id="a2_dag1",
    default_args=default_args,
    description="DAG for Modules 1->2->3->4 with PostgresOperator table creation",
    start_date=datetime(2025, 1, 1),
    schedule_interval='@hourly',
    catchup=False
) as dag:

    # Module 1
    task_module1 = PythonOperator(
        task_id="module1_task",
        python_callable=run_module1,
        op_kwargs={"config_path": DEFAULT_CONFIG_PATH},
    )

    # Module 2
    task_module2 = PythonOperator(
        task_id="module2_task",
        python_callable=run_module2,
        op_kwargs={"config_path": DEFAULT_CONFIG_PATH},
    )

    # Module 3
    task_module3 = PythonOperator(
        task_id="module3_task",
        python_callable=run_module3,
        op_kwargs={"config_path": DEFAULT_CONFIG_PATH},
    )

    # PostgresOperator to create tables
    create_tables = PostgresOperator(
        task_id="create_tables",
        postgres_conn_id="tutorial_pg_conn",  # Name of your Airflow Postgres Connection
        sql=create_tables_sql
    )

    # Module 4: Insert stories & write status file
    task_module4 = PythonOperator(
        task_id="module4_task",
        python_callable=run_module4,
        op_kwargs={"config_path": DEFAULT_CONFIG_PATH},
    )

    # Dependencies:
    task_module1 >> task_module2 >> task_module3 >> create_tables >> task_module4
