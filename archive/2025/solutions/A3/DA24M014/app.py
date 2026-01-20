import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageDraw
import requests
import argparse

# Function to send image data to REST API for prediction
def predict(image_vector, api_url):
    try:
        # Send POST request to REST API
        response = requests.post(api_url, json={"image": image_vector})

        if response.status_code == 200:
            result = response.json()
            messagebox.showinfo("Result", f"Digit: {result['predicted_digit']}")
        else:
            messagebox.showerror("Error", f"API Error: {response.json().get('detail')}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to API: {str(e)}")


class DrawingApp:
    def __init__(self, root, api_url):
        self.root = root
        self.api_url = api_url  
        self.root.title("Handwritten Digit Classifier")

        self.canvas_size = 680  
        self.image_size = 28 
        self.brush_size = 20  

        self.canvas = tk.Canvas(root, bg="black", width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        self.image = Image.new("L", (self.image_size, self.image_size), "black")
        self.draw = ImageDraw.Draw(self.image)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()
        
        self.predict_button = tk.Button(self.button_frame, text="Predict", command=self.predict_image)
        self.predict_button.pack(side="left")

        self.clear_button = tk.Button(self.button_frame, text="Clear", command=self.clear_canvas)
        self.clear_button.pack(side="right")

        self.canvas.bind("<B1-Motion>", self.paint)

    def paint(self, event):
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)

        self.canvas.create_oval(x1, y1, x2, y2, fill="yellow", outline="yellow")

        scaled_x1, scaled_y1 = (x1 * self.image_size // self.canvas_size), (y1 * self.image_size // self.canvas_size)
        scaled_x2, scaled_y2 = (x2 * self.image_size // self.canvas_size), (y2 * self.image_size // self.canvas_size)
        self.draw.ellipse([scaled_x1, scaled_y1, scaled_x2, scaled_y2], fill="yellow")

    def predict_image(self):
        image_data = np.array(self.image).reshape(1, -1).tolist()[0]  # Flatten into a list
        predict(image_data, self.api_url)  

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("L", (self.image_size, self.image_size), "black")
        self.draw = ImageDraw.Draw(self.image)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handwritten Digit Classifier UI")
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="The URL of the REST API endpoint (e.g., http://localhost:8000/predict)"
    )
    args = parser.parse_args()

    root = tk.Tk()
    app = DrawingApp(root, args.url)  
    root.mainloop()
