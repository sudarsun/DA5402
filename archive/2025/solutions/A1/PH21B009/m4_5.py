from pymongo import MongoClient
from bson.binary import Binary
import os
import hashlib
import time
from tqdm import tqdm

def connect_database(host = "mongodb://localhost:27017/"):
    # Connect to MongoDB
    client = MongoClient(host)

    # Create/access database and collection (table)
    db = client['image_text_db']

    # connecting to thumbnail and headline table
    img_table = db['thumbnail_table'] 
    headline_table = db['headline_table'] 

    # putting the hash table as unique, so we wont allow duplicates as well
    img_table.create_index([('image_headline_hash', 1)], unique=True)

    return (headline_table, img_table)


# iterating and storing all the images_hash and headlines
def module_4_and_5_store_in_database(root_img, 
                               extracted_data,
                               headline_table,
                               img_table):

    for i,datapoint in tqdm(enumerate(extracted_data)):

        current_headline = datapoint['headline']
        current_image_id = datapoint['image_id']
        current_url = datapoint['image_url']
        current_headline_hash = hashlib.sha256(current_headline.encode('utf-8')).hexdigest()

        # getting the image id
        img_path = f"{root_img}/image_{current_image_id}.jpg"

        # Reading the image data
        with open(img_path, 'rb') as current_img_data:
            # creating the hash of the image
            current_img_hash = hashlib.sha256(current_img_data.read()).hexdigest()
            binary_image = Binary(current_img_data.read())

        # Create table row document
        headline_document = {
            "headline": current_headline,
            "image_url": current_url,
            "image_id": current_image_id,
            "image_index": img_table.count_documents({}),
        }

        img_document = {"image_headline_hash" : current_img_hash + current_headline_hash, 
                        "image_bin" : binary_image}
        
        try:
            # Insert into table of headline and images (will insert only of the hash is unique)
            img_table.insert_one(img_document)
            headline_table.insert_one(headline_document)
        
        except: pass

    print(f"Successfully stored {img_table.count_documents({})} records")


if __name__ == '__main__':

    # # example code here
    # d1, d2 = create_database()
    # print('database created successfully')

    pass