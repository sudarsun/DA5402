#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
Example DAG demonstrating the usage of the classic Python operators to execute Python functions natively and
within a virtual environment.
"""

from __future__ import annotations

import logging
import sys
import time
from pprint import pprint
from bs4 import BeautifulSoup


import pendulum

from airflow.models.dag import DAG
from airflow.operators.python import (
    ExternalPythonOperator,
    PythonOperator,
    PythonVirtualenvOperator,
    is_venv_installed,
)
from airflow.operators.bash import BashOperator

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.filesystem import FileSensor

log = logging.getLogger(__name__)

PATH_TO_PYTHON_BINARY = sys.executable


with DAG(
    dag_id="image_dataset_and_file_creator",
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["periodic_dataset_creator"],
    schedule_interval="0 * * * *"
    
):

    def fun_scrape_home_page(ti=None):
        import sys
        sys.path.append('include')
        from scraper import scrape_home_page
        from config import base_url_and_search_string

        rawHTMLTextData = scrape_home_page(base_url_and_search_string['search_string'], base_url_and_search_string['base_url'])
        ti.xcom_push(key='rawHTMLData', value=rawHTMLTextData)
        


    scrape_home_page = PythonOperator(
        task_id="scrape_home_page",
        python_callable=fun_scrape_home_page,
        provide_context=True
    )

    def fun_scrape_top_stories(ti=None):
        import sys
        sys.path.append('include')
        from scraper import scrape_only_stories
        from config import base_url_and_search_string
        
        
        rawHTMLTextData = ti.xcom_pull(task_ids='scrape_home_page', key='rawHTMLData')
        story_list_html = scrape_only_stories(rawHTMLTextData, base_url_and_search_string['search_string'], base_url_and_search_string['base_url'])
        ti.xcom_push(key="story_list_html", value=story_list_html)



    scrape_top_stories = PythonOperator(
        task_id="scrape_top_stories",
        python_callable=fun_scrape_top_stories,
        provide_context=True
    )

    def fun_extract_story_data(ti=None):
        import sys
        sys.path.append('include')

        from extractor import extract_story_data_list
        story_list_html = ti.xcom_pull(task_ids='scrape_top_stories', key='story_list_html')
        extracted_story_data_list = extract_story_data_list(story_list_html)
        ti.xcom_push(key="extracted_story_data_list", value=extracted_story_data_list)

    extract_story_data = PythonOperator(
        task_id="extract_story_data",
        python_callable=fun_extract_story_data,
        provide_context=True
    )

    create_tables = PostgresOperator(
        task_id="create_tables",
        postgres_conn_id="tutorial_pg_conn",
        sql="""
            CREATE TABLE IF NOT EXISTS imagetable (
                \"imageid\" SERIAL PRIMARY KEY,
                \"imagedata\" BYTEA NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS storydatatable (
                \"storydataid\" SERIAL PRIMARY KEY,
                \"imageid\" integer REFERENCES imagetable (imageid),
                \"headline\" VARCHAR(200),
                \"article_url\" VARCHAR(2000) UNIQUE,
                \"articledate\" TIMESTAMPTZ,
                \"scrapetimestamp\" TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """,
    )

    def fun_insert_stories_into_tables_and_create_file(ti=None):
        from datetime import datetime
        import sys
        sys.path.append('include')
        from config import date_format, status_file_path
        sys.path.pop()
        
        extracted_story_data_list = ti.xcom_pull(task_ids='extract_story_data', key='extracted_story_data_list')
        items_inserted = 0

        try:
            postgres_hook = PostgresHook(postgres_conn_id="tutorial_pg_conn")
            
            for index, story_data in enumerate(extracted_story_data_list):
                try:
                    ##check if headline exists
                    existingHeadlineQuery = f"""
                        SELECT * FROM storydatatable WHERE headline='{story_data['headline'].replace("'", "''")}'
                    """
                    existingHeadline = postgres_hook.get_first(existingHeadlineQuery)
                    if (existingHeadline != None):
                        continue
                    
                    ##insert image into imagetable
                    imageTableInsertionQuery = f"""
                        INSERT INTO imagetable 
                        (imagedata)
                        VALUES
                        (decode('{story_data['image']}', 'base64'))
                    """
                    postgres_hook.run(imageTableInsertionQuery)

                    ##get last inserted imageid
                    getLastImageQuery = f"""
                        SELECT imageid FROM imagetable
                        ORDER BY imageid DESC
                        LIMIT 1;
                    """
                    imageid = int(postgres_hook.get_first(getLastImageQuery)[0])
                    

                    storydataTableInsertQuery = f"""
                        INSERT INTO storydatatable 
                        (imageid, headline, article_url, articledate)
                        VALUES 
                        ({imageid}, '{story_data['headline'].replace("'", "''")}', '{story_data['articleUrl']}', '{datetime.strptime(story_data['articleDate'], date_format)}');
                    """
                    try:
                        postgres_hook.run(storydataTableInsertQuery)
                        items_inserted += 1
                    except Exception as e:
                        deleteDataFromImageTableQuery = f"""
                            DELETE FROM imagetable WHERE imageid={imageid}
                        """

                        postgres_hook.run(deleteDataFromImageTableQuery)
                        raise

                except Exception as e:
                    log.error(f"Error in inserting {index}th record into db")
                    log.error(e)

        except Exception as e:
            log.error(e)

        with open(status_file_path, 'w') as f:
            f.write(str(items_inserted))
            

    insert_stories_into_tables_and_create_file = PythonOperator(
        task_id="insert_stories_into_tables_and_create_file",
        python_callable=fun_insert_stories_into_tables_and_create_file,
        provide_context=True
    )



    
scrape_home_page >> scrape_top_stories >> extract_story_data >> create_tables >> insert_stories_into_tables_and_create_file
