from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pickle
import uvicorn
from dense_neural_class import Dense_Neural_Diy

# Initialize FastAPI app
app = FastAPI()

# Load the pre-trained model
def load_model(filename):
    with open(filename, 'rb') as file:
        model_loaded = pickle.load(file)
    return model_loaded

model = load_model('model.pkl')

# Define input schema for prediction
class ImageData(BaseModel):
    image: list  # A flattened 1D list representing a 28x28 grayscale image

@app.post("/predict")
def predict(image_data: ImageData):
    try:
        # Convert input data to NumPy array and preprocess
        image_vector = np.array(image_data.image).reshape(1, -1) / 255.0

        # Perform prediction using the loaded model
        prediction = model.predict(image_vector)
        predicted_digit = int(prediction[0])  # Get the predicted digit

        return {"predicted_digit": predicted_digit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)