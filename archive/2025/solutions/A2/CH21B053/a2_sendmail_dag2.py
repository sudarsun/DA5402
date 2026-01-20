import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator  # or DummyOperator in older Airflow

STATUS_FILE_PATH = "/opt/airflow/dags/run/status"  # Adjust if needed

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def read_status_file():
    """
    Reads the integer from the status file and returns it.
    """
    with open(STATUS_FILE_PATH, "r", encoding="utf-8") as f:
        val = int(f.read().strip())
    return val

def decide_branch(**context):
    """
    Branches to 'send_email' if the status file > 0, else 'no_email'.
    """
    val = context['ti'].xcom_pull(task_ids='read_status')
    if val > 0:
        return 'send_email'
    else:
        return 'no_email'

def remove_status_file():
    """
    Deletes the status file so the next run starts fresh.
    """
    if os.path.exists(STATUS_FILE_PATH):
        os.remove(STATUS_FILE_PATH)

with DAG(
    dag_id="a2_sendmail_dag2",
    default_args=default_args,
    description="Module 6 DAG: Send email if new rows inserted",
    start_date=datetime(2025, 1, 1),
    schedule_interval='@hourly',   # We only want this DAG triggered by the FileSensor (or externally)
    catchup=False
) as dag:

    # 1. Wait for status file
    #    - The "fs_conn_id" references a Filesystem connection in Airflow
    wait_for_status = FileSensor(
        task_id="wait_for_status",
        fs_conn_id="fs_default",  # Or None if you have a direct path
        filepath="dags/run/status",  # Relative to fs_conn_id's base path
        poke_interval=30,  # check every 30 seconds
        timeout=600,       # fail if not found in 10 minutes
        mode="reschedule"  # or "poke"
    )

    # 2. Read the integer from the status file
    read_status = PythonOperator(
        task_id="read_status",
        python_callable=read_status_file
    )

    # 3. Branch based on the integer
    branch = BranchPythonOperator(
        task_id="branch",
        python_callable=decide_branch,
        provide_context=True
    )

    # 4. Send an email if val > 0
    send_email = EmailOperator(
        task_id="send_email",
        to="YOUR_EMAIL@example.com",   # Replace with your email
        subject="Module 6: New Rows Inserted!",
        html_content="<h3>We found new rows in the DB!</h3>"
    )

    # If val = 0, skip sending an email
    no_email = EmptyOperator(
        task_id="no_email"
    )

    # 5. Cleanup: remove the status file
    cleanup = PythonOperator(
    task_id="cleanup_status",
    python_callable=remove_status_file,
    trigger_rule='none_failed'  # or 'all_done'
)

    # Define the order
    wait_for_status >> read_status >> branch
    branch >> [send_email, no_email] >> cleanup
