#!/usr/bin/python

import spacy

# should run the following command to download the model file.
# python -m spacy download en_core_web_sm
print("loading the model")
nlp_en = spacy.load("en_core_web_sm")

print("processing the text for NPs and NERs")
doc_en = nlp_en("We are learning to build a REST API around an NLP application. We are students of IIT Madras.")

print("NP:", [ch for ch in map(lambda x: x.text, doc_en.noun_chunks)])
print("NE:", dict(map(lambda x: (x.text,x.label_), doc_en.ents)))

