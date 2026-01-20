# Use the official Python image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the required files into the container
COPY new_requirements.txt .

# Install dependencies
RUN pip install -r new_requirements.txt

# Copy the FastAPI app into the container
COPY model.pkl fast_api_backend.py utils.py dense_neural_class.py /app/

# Expose the port FastAPI runs on
EXPOSE 8000

# Run FastAPI using Uvicorn
CMD ["python", "fast_api_backend.py"]