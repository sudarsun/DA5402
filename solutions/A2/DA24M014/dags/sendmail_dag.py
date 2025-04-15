import os
import smtplib
import logging
from datetime import datetime, timedelta
from email.message import EmailMessage

from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator
from airflow.models import Variable

# Email configuration (Stored securely in Airflow Variables)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = Variable.get("email_sender", "abc")
EMAIL_PASSWORD = Variable.get("email_password", "xyz")  # Make sure this is securely stored
EMAIL_RECEIVER = Variable.get("email_receiver", "abc")

# Status file path
STATUS_FILE = Variable.get("status_file_path", "/opt/airflow/dags/run/status")

# DAG default arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 2, 14),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'send_email_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
)

def send_email():
    try:
        if not os.path.exists(STATUS_FILE):
            logging.info("❌ Status file does not exist. Skipping email.")
            return

        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            new_entries = f.read().strip()

        if not new_entries or new_entries == "0":
            logging.info("✅ No new articles added. Skipping email.")
            return

        # Create an email message with UTF-8 encoding
        msg = EmailMessage()
        msg.set_content(f"""
        Hello,

        📰 {new_entries} new articles were added to the database.

        Regards,
        Your Airflow Pipeline
        """, charset="utf-8")

        msg["Subject"] = f"News Update - {new_entries} Articles Added"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email successfully sent: {new_entries} new articles.")

    except Exception as e:
        logging.error(f"❌ Email sending failed: {e}", exc_info=True)

def delete_status_file():
    if os.path.exists(STATUS_FILE):
        os.remove(STATUS_FILE)
        logging.info("🗑 Status file deleted.")
    else:
        logging.warning("⚠ Status file not found. Nothing to delete.")

# FileSensor waits for status file
wait_for_status = FileSensor(
    task_id='wait_for_status_file',
    filepath=STATUS_FILE,
    poke_interval=30,
    timeout=600,
    mode="poke",
    dag=dag,
)

send_email_task = PythonOperator(
    task_id='send_email',
    python_callable=send_email,
    dag=dag,
)

delete_status_task = PythonOperator(
    task_id='delete_status_file',
    python_callable=delete_status_file,
    dag=dag,
)

# Task Workflow
wait_for_status >> send_email_task >> delete_status_task
