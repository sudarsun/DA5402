from selenium import webdriver
import time
from bs4 import BeautifulSoup
import os
import requests
from selenium.webdriver.chrome.options import Options
import tempfile

def extract_thumbnails_and_headlines(top_stories_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    user_data_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(options=chrome_options)
    # driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH
    driver.get(top_stories_url)
    
    # Scroll to load lazy-loaded content
    for _ in range(30):  # Adjust number of scrolls as needed
        driver.execute_script("window.scrollBy(0, 5000);")
        time.sleep(2)  # Wait for content to load
    
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find all articles with specified classes for images and headlines
    articles = soup.find_all('article')
    data = []

     
    for article in articles:
        # Extract image URL using class="Quavad vwBmvb"
        image_tag = article.find('img', class_='Quavad vwBmvb')
        thumbnail = image_tag['src'] if image_tag else None
        if thumbnail and thumbnail.startswith('/api/attachments/'):
            thumbnail = "https://news.google.com" + thumbnail
            if thumbnail[-3:]==' 1x' or thumbnail[-3:]==' 2x' or thumbnail[-3:]==' 3x':
                thumbnail = thumbnail[:-3]
        # Extract headline using class="gPFEn"
        headline_tag = article.find('a', class_='gPFEn')
        headline = headline_tag.text.strip() if headline_tag else None
        news_url = headline_tag['href'] if headline_tag else None
        if news_url and news_url.startswith('./read/'):
            news_url = "https://news.google.com" + news_url[1:]

        writer = article.find('div', class_ = 'bInasb')
        if writer and writer.text.strip().startswith('By'):
            writer = writer.text.strip()[3:]

        if thumbnail and headline and news_url:
            if writer:
                data.append({
                    'Image': thumbnail,
                    'Headline': headline,
                    'News_url':news_url,
                    'writer':writer
                })
            else:
                data.append({
                    'Image': thumbnail,
                    'Headline': headline,
                    'News_url':news_url,
                    'writer':""
                })
    driver.quit()
    return data

def main():
    top_stories_url = input()
    stories_data = extract_thumbnails_and_headlines(top_stories_url)
    print(stories_data)

if __name__ == "__main__":
    main()