import requests
from bs4 import BeautifulSoup
import base64
import datetime
from urllib.parse import urljoin

BASE_URL = "https://news.google.com"

def get_image_as_base64(image_url):
    """Downloads an image and converts it to a Base64-encoded string."""
    try:
        response = requests.get(image_url, timeout=5)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        print(f"⚠️ Error downloading image: {e}")
    return None  # Return None if image can't be processed

def scrape_top_stories():
    """Scrapes top news stories from Google News."""
    url = BASE_URL
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    # Step 1: Get Google News homepage
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Error: Unable to fetch Google News (Status {response.status_code})")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Step 2: Find "Top Stories" section link
    top_stories_tag = soup.select_one("c-wiz div.n3GXRc a.aqvwYd")
    if not top_stories_tag or not top_stories_tag.get("href"):
        print("⚠️ Could not find 'Top Stories' section link.")
        return None

    top_stories_url = urljoin(BASE_URL, top_stories_tag["href"].replace("./", ""))
    print(f"🔗 Found 'Top Stories' page: {top_stories_url}")

    # Step 3: Fetch the Top Stories page
    response = requests.get(top_stories_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Error: Unable to fetch Top Stories page (Status {response.status_code})")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Step 4: Extract news articles
    news_data = []
    scrape_timestamp = datetime.datetime.utcnow().isoformat()  # Current UTC timestamp

    articles = soup.select("c-wiz div")

    for article in articles:
        # Extract headline
        headline_tag = article.select_one("a.gPFEn")
        headline = headline_tag.text.strip() if headline_tag else None

        # Extract image URL and convert to Base64
        image_tag = article.select_one("img[src^='https://']")
        image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else None
        image_base64 = get_image_as_base64(image_url) if image_url else None

        if headline:
            news_data.append((headline, image_base64, scrape_timestamp))  # Only 3 values

    print(f"✅ Scraped {len(news_data)} articles.")
    print(f"🔍 Example Data: {news_data[:3]}")  # Show first 3 for verification

    return news_data
