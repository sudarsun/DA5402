FROM apache/airflow:2.10.4

USER root
RUN apt-get update && apt-get install -y chromium chromium-driver

# Optional: If your code references "google-chrome" specifically,
# you can create a symlink from chromium to google-chrome:
# RUN ln -s /usr/bin/chromium /usr/bin/google-chrome

USER airflow

# Copy and install Python deps
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install Postgres provider for Airflow
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir apache-airflow-providers-postgres

