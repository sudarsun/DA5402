#!/usr/bin/env python3
import os
import time
import argparse
import hashlib
from datetime import datetime
import requests
from pymongo import MongoClient
from bson import Binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def get_mongo_database():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        print("Connected to MongoDB.")
        return client["unique_news"]
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
db = get_mongo_database()

def download_image(url):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return response.content 
        else:
            print(f"Failed to download {url} - HTTP status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url} - {e}")
    return None

def insert_image(db, article_id, image_data, image_url):
    images_collection = db.images
    if image_data:
        images_collection.insert_one({
            "article_id": article_id,
            "image": Binary(image_data),
            "image_url": image_url
        })

def date_to_datetime(d):
    return datetime.combine(d, datetime.min.time())

def generate_article_hash(headline, thumbnail_url, scrape_timestamp):
    normalized_headline = headline.lower().strip()
    combined = normalized_headline + (thumbnail_url or "")
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def insert_data(db, headline, thumbnail_url, scrape_timestamp):
    try:
        articles_collection = db["articles"]
        article_hash = generate_article_hash(headline, thumbnail_url, scrape_timestamp)
        if articles_collection.find_one({"article_hash": article_hash}):
            print("Duplicate article found. Skipping insertion.")
            return
        article_id = articles_collection.insert_one({
            "headline": headline,
            "thumbnail_url": thumbnail_url,
            "scrape_timestamp": scrape_timestamp,
            "article_date": date_to_datetime(datetime.now().date()),
            "article_hash": article_hash
        }).inserted_id
        
        if thumbnail_url:
            image_data = download_image(thumbnail_url)
            if image_data:
                insert_image(db, article_id, image_data, thumbnail_url)
            else:
                print("Failed to download image.")
    except Exception as e:
        print(f"Error inserting data: {e}")

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path=r"C:\Users\SUKRITI\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scroll_page(driver, timeout=120):
    scroll_pause_time = 5 
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_thumbnail_url(image_element):
    srcset = image_element.get_attribute('srcset')
    src = image_element.get_attribute('src')
    if srcset:
        urls = srcset.split(',')
        best_res_url = urls[-1].strip().split(' ')[0]
        return best_res_url if best_res_url.startswith(('http:', 'https:')) else src
    return src

def get_top_stories_link(driver, top_stories_text):
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
    except TimeoutException:
        print("Timeout waiting for page links.")
        return None

    query_text = top_stories_text.lower()
    xpath_expr = (
        f"//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{query_text}')]"
    )
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_expr))
        )
        top_stories_url = element.get_attribute("href")
        print(f"Found Top Stories link: {top_stories_url}")
        return top_stories_url
    except Exception as e:
        print(f"Error finding Top Stories link: {e}")
        return None

def scrape_google_news(url, driver=None):
    own_driver = False
    if driver is None:
        driver = setup_driver()
        own_driver = True
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.IBr9hb")))
        scroll_page(driver)
        articles = driver.find_elements(By.CSS_SELECTOR, "article.IBr9hb")
        print("Article count:", len(articles))
        for index, article in enumerate(articles):
            try:
                headline = article.find_element(By.CSS_SELECTOR, "a.gPFEn").text.strip()
                image_element = article.find_element(By.TAG_NAME, "img")
                thumbnail_url = extract_thumbnail_url(image_element)
                insert_data(db, headline, thumbnail_url, datetime.now())
            except NoSuchElementException:
                print("Missing element in this article.")
    finally:
        if own_driver:
            driver.quit()

def main():
    parser = argparse.ArgumentParser(
        description="Scrape headlines and thumbnails from the Top Stories page by first extracting the link from the home page. "
                    "The Top Stories text is configurable."
    )
    parser.add_argument(
        "--home_url",
        type=str,
        default="https://news.google.com",
        help="Home page URL (default: https://news.google.com)"
    )
    parser.add_argument(
        "--chromedriver",
        type=str,
        default=r"C:\Users\SUKRITI\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe",
        help="Path to the chromedriver executable."
    )
    parser.add_argument(
        "--top_stories_text",
        type=str,
        required=True,
        help="Text to search for the Top Stories link (e.g., 'top stories')"
    )
    args = parser.parse_args()

    driver = setup_driver()
    try:
        driver.get(args.home_url)
        top_stories_link = get_top_stories_link(driver, args.top_stories_text)
        if not top_stories_link:
            print("Could not find Top Stories link. Exiting.")
            return
        print("Using Top Stories link:", top_stories_link)
        scrape_google_news(top_stories_link, driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
