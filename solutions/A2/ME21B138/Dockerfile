# FROM apache/airflow:2.10.5

# # Copy the requirements file into the image
# COPY requirements.txt .

# # Install Airflow (matching the base version) and any additional Python libraries
# RUN pip install --upgrade pip && \
#     pip install apache-airflow==2.10.5 && \
#     pip install -r requirements.txt

FROM apache/airflow:2.10.5

# Switch to root to install system packages
USER root

# Install dependencies required by Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    lsb-release \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils

# Add Google’s official GPG key and repository, then install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch back to the airflow user
USER airflow

# Copy the requirements file into the image
COPY requirements.txt .

# Upgrade pip and install Airflow (matching the base version) and any additional Python libraries
RUN pip install --upgrade pip && \
    pip install apache-airflow==2.10.5 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install apache-airflow-providers-postgres

