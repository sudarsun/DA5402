#!/usr/bin/python

#!pip install spacy fastapi
#!pip install python-multipart

from fastapi import FastAPI, Body, UploadFile, File
from pydantic import BaseModel
import spacy
import uvicorn
import os
import os.path

# get the PORT number from the environment variable
port = os.getenv('REST_API_PORT', '7000')
port = int(port)

nlp_en = spacy.load("en_core_web_sm")
app = FastAPI(title="First AI application with File upload option")

class Data(BaseModel):
    text:str

@app.post("/np")
def extract_np(data:Data):
    doc_en = nlp_en(data.text)
    nps = [ch for ch in map(lambda x: x.text, doc_en.noun_chunks)]
    return {"input":data.text, "NP":nps}

@app.post('/ne')
def extract_ne(data:Data):
    doc_en = nlp_en(data.text)
    ne = dict(map(lambda x: (x.text,x.label_), doc_en.ents))
    return {"input":data.text, "NE":ne}

@app.get('/check')
def check_file():
    if os.path.isfile('/tmp/myfile'):
        with open('/tmp/myfile', 'r') as f:
            text = f.read()
            f.close()
            return process_text(text)
    return {"error":"/tmp/myfile does not exist"}

def process_text(text:str):
    lines = text.split("\n")
    records = []
    for line in lines:
        if line == "":
            continue
        doc_en = nlp_en(line)
        nps = [ch for ch in map(lambda x: x.text, doc_en.noun_chunks)]
        record = {"input":line, "NP":nps}
        records.append(record)
    return {"results": records}

@app.post("/nptext")
async def extract_body(text:str=Body(...)):
    return process_text(text)

@app.post("/upload")
async def extract_ne_from_upload(file: UploadFile = File(...)):
    content_bytes = file.file.read()
    content_text = content_bytes.decode()
    return process_text(content_text)

# Run from command line: uvicorn ai_app:app --port 7000 --host 0.0.0.0
# or invoke the code below.
uvicorn.run(app, host='0.0.0.0', port=port)
