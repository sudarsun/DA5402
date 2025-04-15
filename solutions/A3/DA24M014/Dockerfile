# Use the official Ubuntu 22.04 base image
FROM ubuntu:22.04

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python3, pip, and required system dependencies
RUN apt-get update && apt-get install -y python3 python3-pip python-is-python3 && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Create a working directory for the application
WORKDIR /usr/src/app

# Copy application files into the container
COPY . /usr/src/app/

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for REST API (8000) and UI (7000)
EXPOSE 8000  
EXPOSE 7000  


CMD ["python", "/usr/src/app/api.py"]
