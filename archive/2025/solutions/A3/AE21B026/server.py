import os
import pickle
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from utils import *
from dense_neural_class import *

# Load the model at startup
def load_model(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, filename + '.pkl')
    
    with open(filepath, 'rb') as file:
        model =  pickle.load(file)

    return model

model = load_model('model')


# FastAPI app
app = FastAPI(title="Handwritten Digit Classifier")

# Request data model
class ImageData(BaseModel):
    image_vector: list  # List of pixel values

#Predict the digit and return to the client
@app.post("/predict/")
def predict_digit(data: ImageData):
    image_vector = np.array(data.image_vector).reshape(1, -1)
    prediction = model.predict(image_vector)[0]
    return {"digit": int(prediction)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
