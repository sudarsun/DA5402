#!/usr/bin/env python3
import argparse
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver(chromedriver_path):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_top_stories_link(home_url, top_stories_text, chromedriver_path):
    driver = setup_driver(chromedriver_path)
    try:
        driver.get(home_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        query_text = top_stories_text.lower()
        xpath_expr = (
            f"//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
            f"'{query_text}')]"
        )
        link_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_expr))
        )
        top_stories_url = link_element.get_attribute("href")
        print(f"Found Top Stories link: {top_stories_url}")
        driver.get(top_stories_url)
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete') 
        page_source = driver.page_source
        output_html_file="top_stories.html"
        with open(output_html_file, 'w', encoding='utf-8') as file:
            file.write(page_source)
        print(f"Saved HTML content of Top Stories page to {output_html_file}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
    return top_stories_url

def main():
    parser = argparse.ArgumentParser(
        description="Scrape the 'Top Stories' link from the home page. "
                    "The text to search for is configurable."
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
        help="The text of the link to identify (case-insensitive). E.g., 'top stories'"
    )
    parser.add_argument(
        "--chromedriver",
        type=str,
        default=r"C:\Users\SUKRITI\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe",
        help="The path to the chromedriver executable."
    )
    args = parser.parse_args()

    scrape_top_stories_link(args.home_url, args.top_stories_text, args.chromedriver)

if __name__ == "__main__":
    main()
