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
    dag_id="email_sender_and_file_deleter",
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["periodic_mailer"],
    schedule_interval="0 * * * *"
):
    
    def send_mail(sender, receiver, subject, message, app_password, smtp_server, smtp_port):
        import smtplib

        text = f"SUBJECT: {subject}\n\n{message}"

        mailserver = smtplib.SMTP(smtp_server,smtp_port)
        mailserver.starttls()
        mailserver.login(sender, app_password)

        mailserver.sendmail(sender,receiver,text)

        mailserver.quit()

    def fun_send_mail_and_delete_file():
        import sys
        import os
        sys.path.append("include")
        from config import sender, receiver, app_password, smtp_server, smtp_port, status_file_path
        sys.path.pop()
        
        print("file found")
        file_content = ""
        if (os.path.isfile(status_file_path)):
            with open(status_file_path, "r") as f:
                file_content = f.read().strip()
            os.remove(status_file_path)
            print("file removed")

            if (file_content != "0"):
                subject = "Pipeline data insersion notification"
                message = f"{file_content} - (image, headline) inserted to DB"
                send_mail(sender, receiver, subject, message, app_password, smtp_server, smtp_port)
                print(f"Mail sent to - {receiver}")
            else:
                print("No records inserted as part of the previous pipeline run.")
        else:
            print("can't find file")
    
    send_mail_and_delete_file = PythonOperator(
        task_id="send_mail_and_delete_file",
        python_callable=fun_send_mail_and_delete_file
    )


    sense_file = FileSensor(task_id="wait_for_status_file", filepath="/opt/airflow/dags/status", fs_conn_id="fs_default")

sense_file >> send_mail_and_delete_file