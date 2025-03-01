from tqdm import tqdm
import requests
import os
from m1 import module_1_web_scrapping_with_lazy_loading
import m1

driver = m1.driver

def module_3_thumbnail_img_extraction(top_stories_url,
                                      article_class_name = "MQsxIb xTewfe tXImLc R7GTQ keNKEd keNKEd VkAdve GU7x0c JMJvke q4atFc",
                                      headline_class_name = "ipQwMb ekueJc RD0gLb",
                                      img_class_name = "tvs3Id QwxBBf"):
    
    thumbnail_img_list = []
    print(f"Total pages available to scrap : {len(top_stories_url)}")

    for url in tqdm(top_stories_url):

        # extracting the contents of all pages 
        top_story_page_content = module_1_web_scrapping_with_lazy_loading(url = url)
        
        all_news_cards = top_story_page_content.find_all('article', {'class': article_class_name})

        for news_articles in all_news_cards:
                
                # Extract headline
                headline = news_articles.find('h4', {'class': headline_class_name})
                headline_text = headline.get_text(strip=True) if headline else "None"
                
                # Extracting thumbnails (using src or data-src attr)
                img = news_articles.find('img', {'class': img_class_name})
                # print(img)

                thumbnail_url = None
                if img:
                    thumbnail_url = img.get('src') or img.get('data-src')
                    if thumbnail_url or thumbnail_url.startswith('//'):
                        thumbnail_url = f'https://news.google.com{thumbnail_url}'
                
                thumbnail_img_list.append({
                    'headline': headline_text,
                    'thumbnail': thumbnail_url
                })
    
    return thumbnail_img_list

# m3_thumb_img_test = module_3_thumbnail_img_extraction() -> example

"""
root_img - root path (folder) where all images are stored

"""

def download_and_store_image(heading_url_data, root_img = "images"):

    thumbnail_heading_dataset = []
    image_id_list =  [int(x.split('.')[0].split('_')[-1]) for x in os.listdir(root_img)]
    base_val = sorted(image_id_list)[-1] if len(os.listdir(root_img)) > 0 else 0

    for i,data_point in tqdm(enumerate(heading_url_data)):

        # thumbnail and headline
        image_url = data_point['thumbnail']
        image_headline = data_point['headline']
        image_id = (base_val + i + 1) # (this will be the name of the image as well)

        # getting the image and storing them
        img_data = requests.get(image_url).content
        with open(f"{root_img}/image_{image_id}.jpg", 'wb') as handler:
            handler.write(img_data)
        
        # creating a dict to store the data
        dp = {"headline" : image_headline, "image_id" : image_id, "image_url" : image_url}

        # adding things to the dataset
        thumbnail_heading_dataset.append(dp)

    return thumbnail_heading_dataset