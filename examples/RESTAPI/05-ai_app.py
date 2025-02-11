#!/usr/bin/python

from fastapi import FastAPI, Body
from pydantic import BaseModel
import spacy
import uvicorn

nlp_en = spacy.load("en_core_web_sm")
app = FastAPI(title="First AI application")

class Data(BaseModel):
    text:str

@app.post("/np")
def extract_np(data:Data, lang:str):
    doc_en = nlp_en(data.text)
    nps = [ch for ch in map(lambda x: x.text, doc_en.noun_chunks)]
    return {"input":data.text, "NP":nps, "lang":lang}

@app.post('/ne')
def extract_ne(data:Data):
    doc_en = nlp_en(data.text)
    ne = dict(map(lambda x: (x.text,x.label_), doc_en.ents))
    return {"input":data.text, "NE":ne}

@app.post("/nptext")
async def extract_body(text:str=Body(...)):
    lines = text.split("\n")
    records = []
    for line in lines:
        doc_en = nlp_en(line)
        nps = [ch for ch in map(lambda x: x.text, doc_en.noun_chunks)]
        record = {"input":line, "NP":nps}
        records.append(record)
    return {"results": records}

# Run from command line: uvicorn ai_app:app --port 7000 --host 0.0.0.0
# or invoke the code below.
uvicorn.run(app, host='0.0.0.0', port=7000)