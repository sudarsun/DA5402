# from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def extract_top_stories_link(html):
    soup = BeautifulSoup(html, 'html.parser')
    section_title = 'Top stories'
    link_exist = soup.find('a', class_ = 'aqvwYd', href = True)
    if link_exist:
        print(link_exist['href'])
        link = soup.find('a', class_='aqvwYd', href=True, string=lambda t: t and t.strip() == section_title)

        if link:
            url = link['href']
        else:
            link_text = ''.join(link_exist.find_all(text=True, recursive=False)).strip()
            if link_text == section_title:
                url = link_exist['href']
        
        return f"https://news.google.com{url.lstrip('.')}" if url.startswith('.') else url
    return None
   
def main():
    html = input()
    top_stories_link = extract_top_stories_link(html)
    print(f"Top Stories Link: {top_stories_link}")

if __name__ == "__main__":
    main()