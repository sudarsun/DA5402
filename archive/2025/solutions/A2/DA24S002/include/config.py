database_config = {
    "host": "localhost",
    "port": 5432,
    "database": "annotationDB",
    "user": "postgres",
    "password": "root",
}

base_url_and_search_string = {
    "base_url": "https://news.google.com",
    "search_string": "Top stories"
}

path_config = {
    "image_path": "headlineImages"
}

log_file = {
    "file_name": "news_scraper.log"
}

card_tag = 'c-wiz'
date_format = "%Y-%m-%dT%H:%M:%SZ"
temp_file_name = "tempHtmlFile.html"
base_html_file = "baseHtml.html"
mode_of_execution = 0

sender = "setup app password for a gmail id, and put that mail id here"
receiver = "enter receiver mail id"
app_password = "enter your gmail app password after setting it up" # I have shared a guide on how to generate it for the sender email id
smtp_server = "smtp.gmail.com"
smtp_port = 587
status_file_path = "/opt/airflow/dags/status"