FROM ubuntu:22.04

RUN apt-get update

RUN apt-get install -y python3-pip

RUN pip install --upgrade pip

RUN mkdir -p /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

RUN python3 -m spacy download en_core_web_sm

COPY app.py /usr/src/app/

EXPOSE 7000

CMD ["python3", "/usr/src/app/app.py"]

