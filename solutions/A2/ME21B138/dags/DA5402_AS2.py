from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sensors.filesystem import FileSensor
import pendulum, os, smtplib

from SCRIPTS import module1, module2, module3, module4

def scrape_homepage(ti):
    result = module1.scrape_homepage()
    ti.xcom_push(key='scrape_homepage', value=result)

def extract_top_stories_link(ti):
    homepage_html = ti.xcom_pull(key='scrape_homepage', task_ids='scrape_homepage')
    result = module2.extract_top_stories_link(homepage_html)
    ti.xcom_push(key='extract_top_stories_link', value=result)

def extract_thumbnails_and_headlines(ti):
    top_stories_url = ti.xcom_pull(key='extract_top_stories_link', task_ids='extract_top_stories_link')
    result = module3.extract_thumbnails_and_headlines(top_stories_url)
    ti.xcom_push(key='extract_thumbnails_and_headlines', value=result)

def process_records(ti):
    data = ti.xcom_pull(key = 'extract_thumbnails_and_headlines', task_ids = 'extract_thumbnails_and_headlines')
    result = module4.process_records(data)
    ti.xcom_push(key = 'process_records', value = result)

def write_status(ti):
    new_added_stories = ti.xcom_pull(task_ids = 'insert_data')
    print(new_added_stories)
    module4.write_status(new_added_stories)

with DAG(
    "DA5402_AS2_CREATE_DATABASE",
    default_args={"retries": 2},
    start_date=pendulum.datetime(2025, 1, 1),
    schedule_interval='0 * * * *',
    catchup=False
) as dag:
    scrape_homepage = PythonOperator(
        task_id='scrape_homepage',
        python_callable=scrape_homepage
    )
    extract_top_stories_link = PythonOperator(
        task_id='extract_top_stories_link',
        python_callable=extract_top_stories_link
    )
    extract_thumbnails_and_headlines = PythonOperator(
        task_id='extract_thumbnails_and_headlines',
        python_callable=extract_thumbnails_and_headlines
    )
    create_tables = SQLExecuteQueryOperator(
        task_id='create_tables',
        conn_id='tutorial_pg_conn',
        sql="""
            -- Table to store base64 encoded image data.
            CREATE TABLE IF NOT EXISTS images (
                image_id SERIAL PRIMARY KEY,
                image_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );

            -- Table to store headlines and article metadata.
            CREATE TABLE IF NOT EXISTS headlines (
                headline_id SERIAL PRIMARY KEY,
                Headline TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                writer TEXT, 
                scrape_timestamp TIMESTAMP DEFAULT NOW(),
                image_id INTEGER REFERENCES images(image_id)
            );
        """,
        autocommit=True,  # Optional: include if your database requires autocommit
    )
    process_records = PythonOperator(
        task_id = 'process_records',
        python_callable = process_records
    )

    insert_data = SQLExecuteQueryOperator(
        task_id='insert_data',
        conn_id='tutorial_pg_conn',
        sql="""
            DROP TABLE IF EXISTS tmp_total;
            CREATE TEMP TABLE tmp_total(total_new_entries int);

            DO $$
            DECLARE 
            total_new_entries int := 0;
            rec_new int;
            BEGIN
            {% set rec_list = ti.xcom_pull(key='process_records', task_ids='process_records') | default([]) %}
            {% for rec in rec_list %}
            WITH ins_img AS (
                INSERT INTO images (image_data)
                VALUES ('{{ rec.Image | replace("'", "''") }}')
                ON CONFLICT DO NOTHING
                RETURNING image_id
            ),
            selected_image AS (
                SELECT image_id FROM images 
                WHERE image_data = '{{ rec.Image | replace("'", "''") }}' 
                LIMIT 1
            ),
            ins_headline AS (
                INSERT INTO headlines (Headline, url, writer, image_id)
                VALUES (
                    '{{ rec.Headline | replace("'", "''") }}',
                    '{{ rec.News_url | replace("'", "''") }}',
                    '{{ rec.writer | replace("'", "''") }}',
                    (SELECT image_id FROM selected_image)
                )
                ON CONFLICT DO NOTHING
                RETURNING headline_id
            )
            SELECT 
                (SELECT COUNT(*) FROM ins_headline)
            INTO rec_new;
            
            total_new_entries := total_new_entries + rec_new;
            {% endfor %}
            INSERT INTO tmp_total VALUES (total_new_entries);
            END $$;

            SELECT total_new_entries FROM tmp_total;
        """,
        autocommit=True,
        do_xcom_push=True,
    )



    write_status_file = PythonOperator(
        task_id='write_status',
        python_callable=write_status
    )

    
    scrape_homepage>>extract_top_stories_link>>extract_thumbnails_and_headlines>>process_records
    [process_records, create_tables] >> insert_data >> write_status_file


SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = '1@gmail.com'
SMTP_PASSWORD = '1'
MY_EMAIL = '1@gmail.com'

STATUS_FILE_PATH = 'dags/run/status'

def send_email_notification():
    if os.path.exists(STATUS_FILE_PATH):
        with open(STATUS_FILE_PATH, 'r') as f:
            content = f.read().strip()
        try:
            new_rows = int(content)
        except ValueError:
            new_rows = 0
        
        if new_rows > 0:
            subject = "New Articles Alert"
            message = (f"A total of {new_rows} new <image, headline> tuples have been added to the database.")
            email_body = f"Subject: {subject}\n\n{message}"

            try:
                server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
                server.starttls()  # Use TLS for security
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_USERNAME, MY_EMAIL, email_body)
                server.quit()
                print("Email sent successfully.")
            except Exception as e:
                print("Error sending email:", e)
        else:
            print("No new articles to report.")
    else:
        print("Status file not found.")

def delete_status_file():
    if os.path.exists(STATUS_FILE_PATH):
        os.remove(STATUS_FILE_PATH)
        print("Status file deleted.")
    else:
        print("Status file not found; nothing to delete.")


with DAG(
    "DA5402_AS2_SEND_MAIL",
    default_args={"retries": 2},
    start_date=pendulum.datetime(2025, 1, 1),
    schedule_interval='0 * * * *',
    catchup=False
) as dag:
    
    status_file_checkup = FileSensor(
        task_id = 'status_file_checkup',
        fs_conn_id = 'fs_default',
        filepath = 'dags/run/status',
        poke_interval = 30,
        timeout = 1200
    )
    send_email_notification = PythonOperator(
        task_id = 'send_email_notification',
        python_callable = send_email_notification
    )
    delete_status_file = PythonOperator(
        task_id='delete_status_file',
        python_callable=delete_status_file
    )
    status_file_checkup >> send_email_notification
    send_email_notification>>delete_status_file