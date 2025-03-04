#!/usr/bin/python

# run this to pull the nlp model
# python -m spacy download en_core_web_sm

# Once the server is up, visit http://localhost:7000/docs to access the APIs

from fastapi import FastAPI, Body, Request
from pydantic import BaseModel
import spacy
import uvicorn
import time

from prometheus_client import Summary, start_http_server, Counter, Gauge
#from prometheus_client import disable_created_metrics

# disable _created metric.
#disable_created_metrics()

REQUEST_DURATION = Summary('api_timing', 'Request duration in seconds')
counter = Counter('api_call_counter', 'number of times that API is called', ['endpoint', 'client'])
gauge = Gauge('api_runtime_secs', 'runtime of the method in seconds', ['endpoint', 'client']) 
nlp_en = spacy.load("en_core_web_sm")
app = FastAPI(title="First AI application")

class Data(BaseModel):
    text:str

@REQUEST_DURATION.time()
@app.post("/np")
def extract_np(data:Data, lang:str, request:Request):
    counter.labels(endpoint='/np', client=request.client.host).inc()

    start = time.time()
    doc_en = nlp_en(data.text)
    nps = [ch for ch in map(lambda x: x.text, doc_en.noun_chunks)]
    time_taken = time.time() - start

    gauge.labels(endpoint='/np', client=request.client.host).set(time_taken)

    return {"input":data.text, "NP":nps, "lang":lang}

@app.post('/ne')
def extract_ne(data:Data, request:Request):
    counter.labels(endpoint='/ne', client=request.client.host).inc()
    doc_en = nlp_en(data.text)
    ne = dict(map(lambda x: (x.text,x.label_), doc_en.ents))
    return {"input":data.text, "NE":ne}

@app.post("/nptext")
async def extract_body(text:str=Body(...), request:Request=None):
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
start_http_server(18000)

# Run from command line: uvicorn ai_app:app --port 7000 --host 0.0.0.0
# or invoke the code below.
uvicorn.run(app, host='0.0.0.0', port=7000)
