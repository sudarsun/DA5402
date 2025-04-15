FROM python:3.10-slim

# create the app folder inside the docker image.
RUN mkdir -p /usr/src/app

# the list of python packages to install
COPY requirements.txt /usr/src/app/

# install the requirements for the REST API to work
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

# copy the application to the image
COPY server.py /usr/src/app/
COPY utils.py /usr/src/app/
COPY dense_neural_class.py /usr/src/app/
COPY model.pkl /usr/src/app/

EXPOSE 7000

# the startup command for the docker image
CMD ["python3", "/usr/src/app/server.py"]

