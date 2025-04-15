from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile



def scrape_homepage():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    user_data_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://news.google.com')
    html_content = driver.page_source
    driver.quit()
    return html_content
def main():
    scrape_homepage()

if __name__ == "__main__":
    main()