#!/usr/bin/env python3
import argparse
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_driver(chromedriver_path):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_page(url, chromedriver_path, output_file):
    driver = setup_driver(chromedriver_path)
    driver.get(url)
    time.sleep(5)
    page_source = driver.page_source
    driver.quit()
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(page_source)
    print(f"Page source saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Scrape the complete page source of a given URL using Selenium. "
                    "All parameters are configurable via command line."
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://news.google.com",
        help="URL of the page to scrape (default: https://news.google.com)"
    )
    parser.add_argument(
        "--chromedriver",
        type=str,
        default=r"C:\Users\SUKRITI\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe",
        help="Path to the chromedriver executable."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="page_source.html",
        help="File path to save the scraped page source (default: page_source.html)"
    )
    args = parser.parse_args()

    print(f"Scraping URL: {args.url}")
    scrape_page(args.url, args.chromedriver, args.output)

if __name__ == "__main__":
    main()
