#!/usr/bin/python

#!pip install spacy fastapi uvicorn

from fastapi import FastAPI
import uvicorn

# create the webapp.
app = FastAPI(title="My First REST API Server")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q:str=None):
    return {"item_id": item_id, "q": q}

uvicorn.run(app, host='0.0.0.0', port=7000)
