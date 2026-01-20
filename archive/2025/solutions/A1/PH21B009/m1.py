from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import time

# getting the webdriver
# Make sure you have ChromeDriver installed
driver = webdriver.Chrome() 
chrome_options = Options()


def is_page_loaded(driver):
    return driver.execute_script("return document.readyState") == "complete"


def module_1_web_scrapping_with_lazy_loading(driver = driver, url = "https://news.google.com/"):
    
    # getting the url
    driver.get(url)
    time.sleep(1)

    # simulating scrolling for webpage and load-more button
    # getting the last scroll height
    old_items = len(driver.find_elements(By.CSS_SELECTOR, ".item-class, div, article, li"))
    last_height = driver.execute_script(
        "return Math.max(document.documentElement.scrollHeight, document.body.scrollHeight, document.documentElement.clientHeight);")

    # maximum scroll iterations allowed is 5
    scroll_iterations = 0

    while scroll_iterations < 5:

        driver.execute_script("""window.scrollBy(0, Math.max(document.documentElement.scrollHeight, 
                              document.body.scrollHeight, document.documentElement.clientHeight));""")
        time.sleep(1)

        # Loop to check loading status and we will wait for maximum of 5 seconds to load the page
        timeout = 5  # seconds
        start_time = time.time()

        while not is_page_loaded(driver):
            if time.time() - start_time > timeout:
                print("Timeout reached. The page is still loading.")
                break
            time.sleep(0.5)

        # checking for load more button as well
        try:
            load_more_button = driver.find_element(By.CLASS_NAME, "load-more-button")
            load_more_button.click()
            time.sleep(2)
        except : pass

        # getting the new height and new items
        new_items = len(driver.find_elements(By.CSS_SELECTOR, ".item-class, div, article, li"))
        new_height = driver.execute_script(
        "return Math.max(document.documentElement.scrollHeight, document.body.scrollHeight, document.documentElement.clientHeight);")

        # if the heights are same and the page is loaded , then we do timeout
        if (new_height == last_height) and is_page_loaded(driver) and (new_items == old_items):
            break

        # updating the height and scroll_iterations
        last_height = new_height
        old_items = new_items
        scroll_iterations += 1
    
    ## Now extracting the contents using beautifulsoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup

if __name__ == '__main__':
    # example run
    # page_content_module_1 = module_1_web_scrapping_with_lazy_loading()
    # uncomment these 2 lines to run the example
    pass