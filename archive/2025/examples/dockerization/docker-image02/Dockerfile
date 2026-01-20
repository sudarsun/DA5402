FROM python:3.10-slim

# create the app folder inside the docker image.
RUN mkdir -p /usr/src/app

# the list of python packages to install
COPY requirements.txt /usr/src/app/

# install the requirements for the REST API to work
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

# we are using spacy's POS tagger as an example to expose a REST API
RUN python3 -m spacy download en_core_web_sm

# copy the application to the image
COPY app.py /usr/src/app/

# docker application will expose port number 7000
EXPOSE $REST_API_PORT

# the startup command for the docker image
CMD ["python3", "/usr/src/app/app.py"]

