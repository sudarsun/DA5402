#!/usr/bin/env python3
import os
import time
import argparse
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def setup_driver(chromedriver_path):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage") 
    service = Service(executable_path=chromedriver_path)
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
        if best_res_url.startswith(('http:', 'https:')):
            return best_res_url
    return src

def download_image(url, folder="downloaded_images", file_name="image"):
    if url:
        file_path = os.path.join(folder, f"{file_name}.jpg")
        if not os.path.exists(folder):
            os.makedirs(folder)
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded {file_path}")
            else:
                print(f"Failed to download {url} - HTTP status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url} - {e}")

def get_top_stories_link(driver, top_stories_text):
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
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
    except TimeoutException:
        print("Timeout: Could not find Top Stories link.")
        return None

def scrape_top_stories_page(driver):
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.IBr9hb")))
        initial_count = len(driver.find_elements(By.CSS_SELECTOR, "article.IBr9hb"))
        print("Initial article count:", initial_count)
        scroll_page(driver)
        time.sleep(5)
        articles = driver.find_elements(By.CSS_SELECTOR, "article.IBr9hb")
        print("Article count after scrolling:", len(articles))
        for index, article in enumerate(articles):
            try:
                headline = article.find_element(By.CSS_SELECTOR, "a.gPFEn").text.strip()
                image_element = article.find_element(By.TAG_NAME, "img")
                thumbnail_url = extract_thumbnail_url(image_element)
                if thumbnail_url:
                    print(f"Headline: {headline}\nThumbnail: {thumbnail_url}")
                    download_image(thumbnail_url, file_name=f"headline_{index}")
                else:
                    print(f"Headline: {headline}\nNo valid thumbnail URL found.")
            except NoSuchElementException:
                print("Missing element in this article.")
    except TimeoutException:
        print("Timeout waiting for articles to load.")
    return article

def main():
    parser = argparse.ArgumentParser(
        description="Scrape headlines and download thumbnails from the Top Stories page. "
                    "The Top Stories link is extracted from the home page using a configurable text parameter."
    )
    parser.add_argument(
        "--home_url",
        type=str,
        default="https://news.google.com",
        help="The home page URL to scrape (default: https://news.google.com)"
    )
    parser.add_argument(
        "--top_stories_text",
        type=str,
        required=True,
        help="The text to search for the Top Stories link (e.g., 'top stories')"
    )
    parser.add_argument(
        "--chromedriver",
        type=str,
        default=r"C:\Users\SUKRITI\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe",
        help="Path to the chromedriver executable."
    )
    args = parser.parse_args()

    driver = setup_driver(args.chromedriver)
    try:
        driver.get(args.home_url)
        top_stories_link = get_top_stories_link(driver, args.top_stories_text)
        if top_stories_link:
            driver.get(top_stories_link)
            scrape_top_stories_page(driver)
        else:
            print("Could not extract Top Stories link; exiting.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
