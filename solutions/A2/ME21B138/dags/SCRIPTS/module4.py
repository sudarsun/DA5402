import requests
import base64
import os

def process_records(data):
    for record in data:
        image_url = record.get("Image")
        if image_url:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                encoded_image = base64.b64encode(response.content)
                image = encoded_image.decode("utf-8")
        record["Image"] = image
    return data

def write_status(result):
    try:
        # The SQL query returns a list of rows, so extract the first column of the first row.
        total_inserts = int(result[0][0]) if result and result[0] else 0
    except Exception:
        total_inserts = 0
        
    directory = "dags/run"
    os.makedirs(directory, exist_ok=True)
    status_file = os.path.join(directory, "status")
    with open(status_file, "w") as f:
        f.write(str(total_inserts))
    print(f"Status file written with total inserts: {total_inserts}")


def main():
    data = input()
    data = process_records(data)

if __name__ == "__main__":
    main()