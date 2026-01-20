import tkinter as tk
from tkinter import messagebox
import numpy as np
import requests
from PIL import Image, ImageDraw
import argparse


# FastAPI server URL


parser = argparse.ArgumentParser(description="Digit Classifier")
parser.add_argument('--api_url',
                        type=str,
                        default="http://127.0.0.1:7000/predict/", 
                        help='URL to the server')
args = parser.parse_args()

API_URL = args.api_url

# Function to send image data to FastAPI server for prediction
def predict(image_vector):
    response = requests.post(API_URL, json={"image_vector": image_vector.tolist()})
    if response.status_code == 200:
        result = response.json()["digit"]
        messagebox.showinfo("Result", f"Digit: {result}")
    else:
        messagebox.showerror("Error", "Failed to get a prediction.")

# Drawing application class
class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Drawing Canvas 28x28")

        # Canvas settings
        self.canvas_size = 680
        self.image_size = 28
        self.brush_size = 20

        # Canvas for drawing
        self.canvas = tk.Canvas(root, bg="black", width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        # Image for processing
        self.image = Image.new("L", (self.image_size, self.image_size), "black")
        self.draw = ImageDraw.Draw(self.image)

        # Buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()
        
        self.predict_button = tk.Button(self.button_frame, text="  Predict The Digit  ", command=self.predict_image)
        self.predict_button.pack(side="left")

        self.clear_button = tk.Button(self.button_frame, text="  Erase  ", command=self.clear_canvas)
        self.clear_button.pack(side="right")

        # Drawing event
        self.canvas.bind("<B1-Motion>", self.paint)

    def paint(self, event):
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        self.canvas.create_oval(x1, y1, x2, y2, fill="yellow", outline="yellow")

        # Scale drawing to 28x28
        scaled_x1, scaled_y1 = (x1 * self.image_size // self.canvas_size), (y1 * self.image_size // self.canvas_size)
        scaled_x2, scaled_y2 = (x2 * self.image_size // self.canvas_size), (y2 * self.image_size // self.canvas_size)
        self.draw.ellipse([scaled_x1, scaled_y1, scaled_x2, scaled_y2], fill="yellow")

    def predict_image(self):
        image_data = np.array(self.image).reshape(1, -1) / 255.0
        predict(image_data)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("L", (self.image_size, self.image_size), "black")
        self.draw = ImageDraw.Draw(self.image)

# Start the Tkinter app
root = tk.Tk()
root.tk.call('tk', 'scaling', 4.0)
app = DrawingApp(root)
root.mainloop()
