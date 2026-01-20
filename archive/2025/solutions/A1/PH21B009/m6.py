import m1
import m2
import m3
import m4_5
import yaml # type: ignore
import os
import logging

# Creating a logger and setting a file handler
m6_logger = logging.getLogger('m6_logger')
m6_logger.setLevel(logging.DEBUG)

# file handler part
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'config and log/info_log_file.log'))
file_handler.setLevel(logging.DEBUG)

# log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
if not m6_logger.hasHandlers(): m6_logger.addHandler(file_handler)

def module_6_orchestrator(url = "https://news.google.com/", # for m1
                          section = 'stories', # for m2
                          article_class_name = "MQsxIb xTewfe tXImLc R7GTQ keNKEd keNKEd VkAdve GU7x0c JMJvke q4atFc", # for m3
                          headline_class_name = "ipQwMb ekueJc RD0gLb", # for m3
                          img_class_name = "tvs3Id QwxBBf", # for m3
                          host = "mongodb://localhost:27017/", # for m4
                          root_img = "images", # for m4 and m3
                          ):
    
    # getting the base google news page
    try: 
        google_news_page_soup = m1.module_1_web_scrapping_with_lazy_loading(url = url)
        m6_logger.info("Scraping of google news successfully completed")
    except Exception as e:
        print("error occurred") ; 
        m6_logger.exception(e)

    # extracting the links from the soup
    try : 
        top_story_links = m2.module_2_stories_link(soup = google_news_page_soup, section = section)[:1]
        m6_logger.info("Retrieved top-stories links from scrapped Google news page")
    except Exception as e:
        print("error occurred") ; 
        m6_logger.exception(e)

    # now extracting stories , thumbnail from that
    try : 
        headline_thumbnail_url_list = m3.module_3_thumbnail_img_extraction(top_stories_url = top_story_links,
                                                                      article_class_name = article_class_name,
                                                                      headline_class_name = headline_class_name,
                                                                      img_class_name = img_class_name)
        m6_logger.info(f"{len(headline_thumbnail_url_list)} headline and thumbnail urls have been collected")
    except Exception as e:
        print("error occurred") ; 
        m6_logger.exception(e)
    
    print(f"{len(headline_thumbnail_url_list)} headline and thumbnail urls have been collected")

    # now downloading and saving those images
    try : 
        headline_downloaded_img = m3.download_and_store_image(heading_url_data = headline_thumbnail_url_list,
                                                              root_img = root_img)
        m6_logger.info(f"{len(headline_downloaded_img)} has been downloaded successfully")
        
    except Exception as e:
        print("error occurred") ; 
        m6_logger.exception(e) 
    
    print(f"{len(headline_downloaded_img)} has been downloaded successfully")

    # now storing them to the database
    try:
        headline_table, img_table = m4_5.connect_database(host = host)
        prev_table_size = headline_table.count_documents({})

        # storing in database
        m4_5.module_4_and_5_store_in_database(root_img = root_img, 
                                        extracted_data = headline_downloaded_img,
                                        headline_table = headline_table, 
                                        img_table = img_table)
        
        curr_table_size = headline_table.count_documents({})
        m6_logger.info(f"{curr_table_size - prev_table_size} rows has been populated in database")

    except Exception as e:
        print("error occurred") ; 
        m6_logger.exception(e)  

    print(f"{curr_table_size - prev_table_size} rows has been populated in database")


if __name__ == "__main__":

    # all configuration parameters
    with open(os.path.join(os.path.dirname(__file__), 'config and log/All_Parameters_config.yaml'), 'r') as stream:
        params = yaml.safe_load(stream)

    params['root_img'] = os.path.join(os.path.dirname(__file__), params['root_img'])

    # checking the output directory is not there or not creating a new one
    if not os.path.exists(params['root_img']): os.mkdir(params['root_img'])

    module_6_orchestrator(**params)