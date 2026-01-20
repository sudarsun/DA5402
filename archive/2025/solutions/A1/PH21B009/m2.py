import re

def module_2_stories_link(soup, section = 'stories'):

    story_links = soup.find_all('a', href=re.compile(f'^./{section}/')) 

    # for saving the links
    top_story_links = []

    # getting all the links
    for links in story_links:
        story_url = f"https://news.google.com{links['href'].lstrip('.')}"
        top_story_links.append(story_url)
    
    print(f"Total number of stories link extracted : {len(top_story_links)}")

    return top_story_links

# m2_top_story_links = module_2_stories_link(soup = page_content_module_1, section = 'stories') -> example