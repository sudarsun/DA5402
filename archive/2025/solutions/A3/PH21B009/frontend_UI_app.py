import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
from utils import *
from dense_neural_class import *

import io
import requests
import argparse

""" 
Used the code from app.py in github repo
send_and_predict :
    - This function is used to send the image and get the prediction from the backend
    - io.BytesIO() has been used to convert the image into bytes (so it can be json serializable)
"""
# Drawing application class
class DrawingApp:
    def __init__(self, root, url = "http://127.0.0.1:8000/predict"):
        self.root = root
        self.root.title("My Drawing Canvas 28x28")
        self.url = url

        # Canvas settings
        self.canvas_size = 450  # Canvas size in pixels
        self.image_size = 28  # Image size for vectorization
        self.brush_size = 20  # Size of the white brush

        # Canvas for drawing
        self.canvas = tk.Canvas(root, bg="black", width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        # Creation of the image and the object for drawing
        self.image = Image.new("L", (self.image_size, self.image_size), "black")
        self.draw = ImageDraw.Draw(self.image)

        # Action buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()
        
        self.predict_button = tk.Button(self.button_frame, text="  Predict The Digit  ", command=self.send_and_predict)
        self.predict_button.pack(side="left")

        self.clear_button = tk.Button(self.button_frame, text="  Erase  ", command=self.clear_canvas)
        self.clear_button.pack(side="right")

        # Drawing event
        self.canvas.bind("<B1-Motion>", self.paint)

    def paint(self, event):
        # Draw on the screen and on the image
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        
        # Draw on the canvas (screen) with a white brush
        self.canvas.create_oval(x1, y1, x2, y2, fill="yellow", outline="yellow")

        # Draw on the 28x28 image for vectorization
        scaled_x1, scaled_y1 = (x1 * self.image_size // self.canvas_size), (y1 * self.image_size // self.canvas_size)
        scaled_x2, scaled_y2 = (x2 * self.image_size // self.canvas_size), (y2 * self.image_size // self.canvas_size)
        self.draw.ellipse([scaled_x1, scaled_y1, scaled_x2, scaled_y2], fill="yellow")

    def clear_canvas(self):
        # Clears the canvas and creates a new black image
        self.canvas.delete("all")
        self.image = Image.new("L", (self.image_size, self.image_size), "black")
        self.draw = ImageDraw.Draw(self.image)

    """ New function is added here """
    def send_and_predict(self):
        img_bytes = io.BytesIO()
        self.image.save(img_bytes, format="PNG")  # Convert to bytes
        img_bytes.seek(0)

        # Send to FastAPI server
        files = {"file": ("digit.png", img_bytes, "image/png")}
        response = requests.post(self.url, files=files)

        print("response : ", response.json())

        if response.status_code == 200:
            result = response.json().get("digit", "Unknown")  # Extract predicted digit
            messagebox.showinfo("Prediction", f"The digit is: {result}")  # Show popup
        else:
            messagebox.showerror("Error", "Failed to get prediction!")  # Error popup

# Application initialization
# root = tk.Tk()
# root.tk.call('tk','scaling',4.0)
# app = DrawingApp(root)
# root.mainloop()

def main(url = "http://127.0.0.1:8000/predict"):
    root = tk.Tk()
    root.tk.call('tk','scaling',4.0)
    app = DrawingApp(root, url)
    root.mainloop()

if __name__ == '__main__':

    # to get argument from the command line
    parser = argparse.ArgumentParser(description="Drawing App with API URL as an argument.")
    parser.add_argument("--url", type=str, required=False, help="FastAPI prediction endpoint URL.", default = "http://127.0.0.1:8000/predict")
    args = parser.parse_args()

    # This will run the UI app
    main(url = args.url)