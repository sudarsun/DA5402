#!/usr/bin/python

# run this to pull the nlp model
# python -m spacy download en_core_web_sm

# Once the server is up, visit http://localhost:7000/docs to access the APIs

from fastapi import FastAPI, Body, Request
from pydantic import BaseModel
import spacy
import uvicorn
import logging

from prometheus_client import Summary, start_http_server, Counter, Gauge, Info
from prometheus_client import disable_created_metrics

# disable **_created metric.
disable_created_metrics()

request_size = Summary('input_bytes', 'input data size (bytes)')  # _sum will track the total bytes, _count will track the number of calls.
api_usage = Summary('api_runtime', 'api run time monitoring') # _sum tracks total time taken, _count tracks number of calls.

# define the counter to track the usage based on client IP.
counter = Counter('api_call_counter', 'number of times that API is called', ['endpoint', 'client'])

# we didn't use this metric yet.
gauge = Gauge('api_runtime_secs', 'runtime of the method in seconds', ['endpoint', 'client']) 

# add build information to the info metric.
info = Info('my_build', 'Prometheus Instrumented AI App')
info.info({'version': '0.0.13', 'buildhost': '@resonance', 'author': 'Dr. Su Sa', 'builddate': 'March 2025'})

# load up the Spacy NER processor
nlp_en = spacy.load("en_core_web_sm")

# create the AI application
app = FastAPI(title="First AI application")

# Setup the logging mechanism.
log = logging.getLogger("AI_app")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
log.addHandler(ch)

class Data(BaseModel):
    text:str

# NOTE: If the order of the decorator is swapped, api_usage does not work.
@app.post("/np")
@api_usage.time()
def extract_np(data:Data, request:Request, lang:str="en"):
    log.info(f"extract_np: received {len(data.text)} bytes on input")
    
    # let's track the amount of data processed by this API.
    request_size.observe(amount=len(data.text))
    # increment the counter per host per api.
    counter.labels(endpoint='/np', client=request.client.host).inc()

    doc_en = nlp_en(data.text)
    nps = [ch for ch in map(lambda x: x.text, doc_en.noun_chunks)]

    # report the running time of the api.
    #gauge.labels(endpoint='/np', client=request.client.host).set(time_taken)

    return {"input":data.text, "NP":nps, "lang":lang}

@app.post('/ne')
def extract_ne(data:Data, request:Request):
    log.info(f"extract_ne: received {len(data.text)} bytes on input")

    # let's track the amount of data processed by this API.
    request_size.observe(amount=len(data.text))
    # increment the counter per host per api.
    counter.labels(endpoint='/ne', client=request.client.host).inc()

    with api_usage.time():
        doc_en = nlp_en(data.text)
        ne = dict(map(lambda x: (x.text,x.label_), doc_en.ents))

    # report the running time of the api.
    #gauge.labels(endpoint='/np', client=request.client.host).set(time_taken)

    return {"input":data.text, "NE":ne}

# NOTE: If the order of the decorator is swapped, api_usage does not work.
@app.post("/nptext")
@api_usage.time()
def extract_body(text:str=Body(...), request:Request=None):  # the ... (ellipses) operator is a placeholder.
    log.info(f"extract_body: received {len(text)} bytes on input")

    # let's track the amount of data processed by this API.
    request_size.observe(amount=len(text))
    # increment the counter per host per api.
    counter.labels(endpoint='/nptext', client=request.client.host).inc()
    lines = text.split("\n")
    records = []
    for line in lines:
        doc_en = nlp_en(line)
        nps = [ch for ch in map(lambda x: x.text, doc_en.noun_chunks)]
        record = {"input":line, "NP":nps}
        records.append(record)
    return {"results": records}

# start the exporter metrics service
log.info("starting the prometheus monitor at port 18000")
start_http_server(18000)

# start the fastapi server at 7000
uvicorn.run(app, host='0.0.0.0', port=7000)
