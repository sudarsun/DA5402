import psycopg2
import io
from PIL import Image
from config import CONFIG

# Not Related to Assignment, Just to check if the image is stored in the database.

def retrieve_image(headline_id, db_config):
    """Retrieve and reconstruct an image from the database."""
    try:
        conn = psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"]
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT thumbnail FROM images WHERE headline_id = %s;", (headline_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if result and result[0]:
            image_data = result[0]  # Binary data
            image = Image.open(io.BytesIO(image_data))
            image.save("retrieved_image.jpg")
            return image
        else:
            print("No image found for the given headline_id.")
            return None
    except Exception as e:
        print(f"Database error while retrieving image: {e}")
        return None

# Example Usage:
headline_id = 1  # Replace with the actual headline ID
image = retrieve_image(headline_id, CONFIG["db_config"])
if image:
    image.show()  # Open the image
    image.save("retrieved_image.jpg")  # Save as a file
