from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import PIL.Image
import io
import numpy as np
from utils import *
from dense_neural_class import *
import pickle
import os
from utils import *

        
# loading the model from the app 
def load_model(filename):

    # Gets the current directory where the script is being executed
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Constructs the full path of the .pkl file
    filepath = os.path.join(current_dir, filename + '.pkl')
    
    with open(filepath, 'rb') as file:
        model_loaded = pickle.load(file)
    
    return model_loaded

# declaring the app
app = FastAPI()
ml_model = load_model('model')

def predict_the_digit(image):

    """blackened part digit recognition"""
    img = PIL.Image.open(io.BytesIO(image)).convert("L")  # Convert to grayscale

    # rescaling the array
    img = np.array(img).reshape(1, -1) / 255.0

    # getting the digit prediction
    digit = ml_model.predict(img)[0]

    return digit

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()
    predicted_digit = predict_the_digit(content)  # Extract the digit

    # returning the response 
    return JSONResponse({"message": "Digit processed successfully", "digit" : str(predicted_digit)})

if __name__ == "__main__":        
    uvicorn.run(app, host="127.0.0.1", port=8000)
