# DA5402 Assignment 1 - Automated News Scraping Pipeline for Image-Caption Dataset Creation  
## Achyutha Munimakula (ph21b004)  

## Overview  
This solution implements a robust MLOps pipeline designed to generate continuous `<image, caption>` tuples from Google News. The system comprises six modular components that handle web scraping, data storage, deduplication, and orchestration, fully compliant with the requirements of DA5402 Assignment #1.  

## Key Features  
- **Config-Driven Operation**: Utilizes YAML and `.env` for configuration  
- **Headless Browser Support**: Powered by Selenium with Chrome  
- **Lazy Loading Handling**: Automatically simulates scrolling for dynamic content  
- **Composite Deduplication**: Employs SHA-256 hashing for combined image and text  
- **MongoDB Storage**: Leverages GridFS for storing images and metadata  
- **Cron-Ready Orchestration**: Includes comprehensive logging for scheduled operations  

---

## Module Implementations  

### 1. Dynamic News Scraping (Module 1)  
**Approach**:  
- Utilizes Selenium WebDriver with headless Chrome  
- Configured via `config.yaml` and `.env`:  
    ```yaml
    scraping:  
        base_url: "https://news.google.com"  
        scraping_url: "https://news.google.com/home?hl=en-US&gl=US&ceid=US:en"  # Base URL to scrape  
        sub_link_name: "Top Stories"  # Name of the sub-link  
        headers: {  
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"  
        }  # Header for ChromeDriver access  
    ```  

**Technical Highlights**:  
- Implements 3-second load buffers for JavaScript rendering  
- Adaptive scrolling to handle dynamically loaded content  
- Integrates BeautifulSoup for efficient HTML parsing  

### 2. Top Stories Extraction (Module 2)  
**Approach**:  
- Extracts text from parsed HTML to locate the required link  

### 3. Lazy-Load Aware Scraping (Module 3)  
**Innovations**:  
- Progressive scroll simulation:  
    ```python  
    while driver.execute_script("return document.body.scrollHeight") > last_height:  
        scroll_to_bottom()  
        time.sleep(2)  
    ```  
- UTC timestamping for temporal analysis  
- Analyzes CSS classes to extract required data from parsed HTML strings:  
    - `hl_class`: "gPFEn"  
    - `thumbnail_class`: "Quavad vwBmvb"  
    - `url_class`: "WwrzSb"  
    - `publish_time_class`: "hvbAAd"  
    - `publisher_class`: "vr1PYe"  

### 4. Multi-Modal Storage (Module 4)  
**Database Design**:  
- Utilizes MongoDB for an optimized and accessible storage solution  

| Container     | Schema Features                     |  
|---------------|-------------------------------------|  
| `fs.files`    | Headline, Scraping Time, Article URL, Publisher, Publishing Date, etc. |  
| `fs.chunks`   | Chunked image data                  |  

**Optimizations**:  
- Employs GridFS for efficient storage of large files through chunking  
- Checks for existing datasets in the database before uploading  
- Indexes `metadata.img_hl_hash` for faster duplication checks  

### 5. Intelligent Deduplication (Module 5)  
**Composite Key Strategy**:  
- `composite_hash = sha256(image) + sha256(headline)`  
- Indexes `metadata.img_hl_hash` for rapid deduplication checks  
- This module is redundant if every data point is checked for duplicates before uploading to the server  

**Process Flow**:  
1. Combines hashes of images and headlines for deduplication analysis  
2. Analyzes data points with identical hashes  
3. Preserves the most recent duplicate  

### 6. Production Orchestration (Module 6)  
**Cron-Ready Features**:  
- File-based logging (`pipeline.log` sample)  
- Error propagation with exit codes  
- Silent mode operation for scheduled executions  

### Miscellaneous  
- In the Top Stories parsed HTML, the CSS classes for each required data field (headline, thumbnail, author, publisher, etc.) were analyzed (stored in `config.yaml`) and reused for other articles  
- For duplication checks, the binary data of images and headlines are independently hashed and merged as strings. This new hash is stored in the metadata alongside other fields, simplifying duplication checks  
- The database was backed up and uploaded using `mongodump` to the folder `Exported MongoDB Database`  
- Module 4 was implemented to render Module 5 unnecessary, as Module 4 checks for duplicates before uploading data to the database. However, Module 5 can still be used to identify duplicates within the database  
- A batch file was created to execute `module6.py` using the respective Conda virtual environment  
- Public configurations, such as the scraped website and sub-link, can be modified in `config.yaml`  

---

## Setup Instructions  

### Requirements  
Python 3.9+, MongoDB 6.0+, Chrome 120+, and a compatible web driver  

### Configuration  
- `.env` template:  
    ```java  
    DB_HOST=localhost
    DB_PORT=27017
    DB_NAME=Thumbnail_Headline_Database
    ```  

### Execution  
Run `module6.py`  