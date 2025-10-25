import csv
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml import etree
from io import StringIO
import time
import pandas as pd
import os

# --- Global Configurations ---
INPUT_CSV_FILE = "links.csv"
OUTPUT_CSV_FILE = "Succes.csv"
SKIPPED_CSV_FILE = "skip.csv" 
FIELD_NAMES = ['ID', 'NAME', 'AUTHOR', 'GENRE', 'TAGS', 'RATING', 'TOTAL RATING', 'STATUS', 
               'TOTAL CHAPTER', 'LATEST CHAPTER', 'URL', 'ALTERNATIVE_NAMES', 'PUBLISHER']
# Limit the detail scraping for demonstration/testing. Set to None for full scrape.
LIMIT_DETAIL_SCRAPE = None
HEADLESS_MODE = True 

NOVEL_XPATHS = {
    'CRITICAL_WAIT_ELEMENT': '//*[@id="novel"]/div[1]/div[1]/div[2]/div/div[1]/h3',
    'NAME': '//*[@id="novel"]/div[1]/div[1]/div[2]/div/div[1]/h3/text()',
    'RATING': '//*[@id="novel"]/div[1]/div[1]/div[3]/div/div[2]/em/strong[1]/span/text()',
    'TOTAL_RATING_COUNT': '//*[@id="novel"]/div[1]/div[1]/div[3]/div/div[2]/em/strong[2]/span/text()',
    'TOTAL_CHAPTER_COUNT': '//div[@id="list-chapter"]//ul[@class="list-chapter"]/li',
    'LATEST_CHAPTER_TITLE': '//div[@class="l-chapter"]/div[@class="item"]/div[@class="item-value"]/a/text()',
    'CHAPTER_TAB_TITLE': '//*[@id="tab-chapters-title"]',
    'AUTHOR': '//ul[@class="info info-meta"]/li[h3[text()="Author:"]]/a/text()',
    'GENRE_LINKS': '//ul[@class="info info-meta"]/li[h3[text()="Genre:"]]/a',
    'STATUS': '//ul[@class="info info-meta"]/li[h3[text()="Status:"]]/a/text()',
    'ALTERNATIVE_NAMES_LI': '//ul[@class="info info-meta"]/li[h3[contains(text(), "Alternative names:")]]',
    'PUBLISHER_LI': '//ul[@class="info info-meta"]/li[h3[contains(text(), "Publishers:")]]',
    'TAGS_LINKS': '//div[@class="tag-container"]/a/text()',
    'CONTENT_MAIN_BLOCK': '//*[@id="novel"]',
    # UPDATED with the specific, precise XPath provided by the user.
    'CLOUDFLARE_CHALLENGE_INPUT': '//*[@id="oplP4"]/div/label/input',
}

# --- Utility Functions (Omitted for brevity, assumed unchanged) ---

def initialize_uc_driver(headless=True):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument('--disable-gpu') 
    options.page_load_timeout = 30
    try:
        driver = uc.Chrome(options=options)
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
        })
        return driver
    except Exception:
        return None

def get_lxml_tree(html_content):
    parser = etree.HTMLParser()
    return etree.parse(StringIO(html_content), parser)

def get_text(tree, xpath):
    element = tree.xpath(xpath)
    if element:
        if isinstance(element[0], str): return element[0].strip()
        elif hasattr(element[0], 'text') and element[0].text is not None: return element[0].text.strip()
    return 'N/A'

def get_multi_value_lxml(tree, xpath):
    """
    FIXED: Handles XPaths that return either element nodes (<a>) or raw text nodes (/text()).
    """
    nodes = tree.xpath(xpath)
    value_list = []
    
    for node in nodes:
        if isinstance(node, str):
            # Case 1: Node is a text string (XPath ended in /text())
            text = node.strip()
        elif hasattr(node, 'text') and node.text is not None:
            # Case 2: Node is an Element (XPath ended in /a)
            text = node.text.strip()
        else:
            continue
            
        if text:
            value_list.append(text)
            
    return ', '.join(value_list) if value_list else 'N/A'

# --- If you use the simpler XPATH without /text() ---
# You should update XPATHS['TAGS_LINKS'] to omit /text()
# 'TAGS_LINKS': '//div[@class="tag-container"]/a', 

# And then simplify the helper function which is much cleaner:
def get_multi_value_elements(tree, xpath):
    """Targets elements (like <a>) and extracts and joins their text."""
    a_tags = tree.xpath(xpath)
    value_list = [a.text.strip() for a in a_tags if a.text and a.text.strip()]
    return ', '.join(value_list) if value_list else 'N/A'

def get_list_item_text_complex(tree, xpath_li, header_text):
    """Extracts raw text content from a complex <li> and strips the header."""
    element = tree.xpath(xpath_li)
    
    # Check if the element list is empty
    if element and len(element) > 0: 
        full_text = element[0].xpath('string()').strip()
        return full_text.replace(header_text, '').strip()
        
    return 'N/A'

def read_links_from_csv(filename):
    # This is a placeholder; actual robust pandas reading should be used.
    try:
        df = pd.read_csv(filename, sep='|', quoting=csv.QUOTE_NONE, skipinitialspace=True)
        if len(df.columns) == 1 and ('ID,URL' in df.columns[0] or 'ID|URL' in df.columns[0]):
             df = pd.read_csv(filename, header=None, names=['Combined'], sep='|', quoting=csv.QUOTE_NONE, skipinitialspace=True)
             df[['ID', 'URL']] = df['Combined'].str.split(r'[|,]', expand=True, n=1).apply(lambda x: x.str.strip())
             df = df[df['URL'].str.startswith('http', na=False)].copy()
             
        if 'ID' in df.columns and 'URL' in df.columns:
            df['ID'] = pd.to_numeric(df['ID'], errors='coerce').astype('Int64')
            df['URL'] = df['URL'].astype(str)
            df.dropna(subset=['ID', 'URL'], inplace=True)
            links_data = df[['ID', 'URL']].to_dict('records')
            print(f"✅ Successfully read {len(links_data)} valid links from '{filename}'.")
            return links_data
        return []
    except Exception: return []


# --- Novel Detail Scraper ---

def scrape_novel_details(novel_url, driver):
    """Scrapes individual novel details using the provided driver instance."""
    detail_url = novel_url + "#tab-chapters-title" 
    # url=detail_url
    # driver.get(url)
    # print(f"Browser opened and navigating to {url}...")
        
    #     # --- CHALLENGE BYPASS LOGIC ---
    # print("Checking for security challenge...")
    # challenge_passed = False
    # start_time = time.time()
    # MAX_TOTAL_WAIT_TIME = 45 # Time limit to resolve the security check

    # while time.time() - start_time < MAX_TOTAL_WAIT_TIME and not challenge_passed:
        
    #     # 1. Attempt to detect successful load (main content visible)
    #     try:
    #         # Give the browser a few seconds to load the final page before checking
    #         WebDriverWait(driver, 3).until(
    #             EC.presence_of_element_located((By.XPATH, NOVEL_XPATHS['CONTENT_MAIN_BLOCK']))
    #         )
    #         if driver.find_elements(By.XPATH, NOVEL_XPATHS['NAME']):
    #             print("Main content loaded. Challenge passed.")
    #             challenge_passed = True
    #             break
    #     except:
    #         pass # Main content is not yet visible, continue to step 2

    #     # 2. Look for the clickable challenge input to emerge and click it
    #     try:
    #         # Waits up to 5s for the specific challenge box to become clickable
    #         challenge_element = WebDriverWait(driver, 20).until(
    #             EC.element_to_be_clickable((By.XPATH, NOVEL_XPATHS['CLOUDFLARE_CHALLENGE_INPUT']))
    #         )
    #         challenge_element.click()
    #         print("Clicked the security challenge checkbox using the specific XPath. Waiting for resolution...")
    #         time.sleep(7) # Wait for processing and potential redirect
    #     except:
    #         time.sleep(1) # Wait and try again
    
    # if not challenge_passed:
    #     print("⚠️ Warning: Could not pass security challenge within 45 seconds. Scraping may fail.")
    # # --- END CHALLENGE BYPASS LOGIC ---
    
    try:
        driver.get(detail_url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, NOVEL_XPATHS['CRITICAL_WAIT_ELEMENT']))
        )
        # Interaction/Scrolling Logic (omitted for brevity, assumed functional)
        
        
        # 4. Data Extraction
        
        # NOTE: Cannot calculate total chapters without running the full scrolling loop logic
        MAX_SCROLLS = 20  # Increased max attempts for extreme cases
        SCROLL_DELAY = 2.5 # Increased delay to give the page time to fetch and render the new batch
        SCROLL_HEIGHT_JS = "window.scrollTo(0, document.body.scrollHeight + 10000); return document.body.scrollHeight;"
        
        last_count = 0
        
        # Initial wait for the chapter list container
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="list-chapter"]'))
        )
        print("Initial chapters visible. Starting resilient scroll...")

        for i in range(MAX_SCROLLS):
            # Execute scroll: scroll far down (scrollHeight + a buffer)
            driver.execute_script(SCROLL_HEIGHT_JS)
            time.sleep(SCROLL_DELAY)

            # Recalculate count
            current_count = len(driver.find_elements(By.XPATH, NOVEL_XPATHS['TOTAL_CHAPTER_COUNT']))
            
            print(f"Scroll {i+1}/{MAX_SCROLLS}: Current chapter count is {current_count}")

            # Check for Stabilization: stop if the count is the same as the last check
            if current_count == last_count:
                print(f"Chapter count stabilized at {current_count}. Stopping scroll.")
                break
            
            # If the count increased, update and continue
            last_count = current_count
        else:
            print(f"Stopped scrolling after {MAX_SCROLLS} attempts without full stabilization. Final count: {last_count}")
        
        # --- End of Scrolling ---
        try:
            # Get the data (HTML content and tree parsing)
            total_chapters = str(last_count)
            html_content = driver.page_source
            tree = get_lxml_tree(html_content)
            name = get_text(tree, NOVEL_XPATHS['NAME'])
            author = get_text(tree, NOVEL_XPATHS['AUTHOR'])
            status = get_text(tree, NOVEL_XPATHS['STATUS'])
            # alt_names='No'
            # publisher="No"
            alt_names = get_list_item_text_complex(tree, NOVEL_XPATHS['ALTERNATIVE_NAMES_LI'], "Alternative names:")
            publisher = get_list_item_text_complex(tree, NOVEL_XPATHS['PUBLISHER_LI'], "Publishers:")
            genre = get_multi_value_lxml(tree, NOVEL_XPATHS['GENRE_LINKS'])
            # tags='no'
            tags = get_multi_value_lxml(tree, NOVEL_XPATHS['TAGS_LINKS'])
            rating_value = get_text(tree, NOVEL_XPATHS['RATING'])
            total_ratings = get_text(tree, NOVEL_XPATHS['TOTAL_RATING_COUNT'])
            latest_chapter = get_text(tree, NOVEL_XPATHS['LATEST_CHAPTER_TITLE'])
            print(total_chapters,name,author,status,alt_names,publisher,genre,tags,
                  rating_value,total_ratings,latest_chapter)
        
            # driver.quit() # Driver cleanup attempt 1

            # ... (LXML parsing and extraction using the robust label-based XPaths) ...

        except KeyboardInterrupt:
            if driver: driver.quit() # Ensure driver quits on user interruption
            raise # Re-raise the interrupt
        except Exception as e:
            print("FUck")
        # 4. Data Extraction
        
        rating = f"{rating_value}/10" if rating_value != 'N/A' else 'N/A'

        scraped_data = {
            'NAME': name, 'AUTHOR': author, 'GENRE': genre, 'TAGS': tags, 'RATING': rating,
            'TOTAL RATING': total_ratings, 'STATUS': status, 'TOTAL CHAPTER': total_chapters,
            'LATEST CHAPTER': latest_chapter, 'URL': novel_url,
            'ALTERNATIVE_NAMES': alt_names, 'PUBLISHER': publisher
        }

        return scraped_data

    except Exception:
        return None

# --- CSV Output Functions ---

def write_details_to_csv(data_list, filename, fieldnames):
    """Writes new data to the main detail CSV, appending if the file already exists."""
    if not data_list: return
    
    df_out = pd.DataFrame(data_list, columns=fieldnames)
    
    # Check if the file exists and is not empty to decide if header should be written
    write_header = not os.path.exists(filename) or os.path.getsize(filename) == 0

    try:
        # Use 'a' (append) mode. Pandas automatically handles the delimiter and quoting.
        df_out.to_csv(
            filename, 
            sep='|', 
            index=False, 
            mode='a', # <<< APPEND MODE
            header=write_header, # Write header only if file is new/empty
            quoting=csv.QUOTE_ALL, # Use QUOTE_ALL to prevent "need to escape" errors
            encoding='utf-8'
        )
        print(f"✅ Successfully wrote {len(data_list)} novel detail entries to **{filename}** (Append)")
    except Exception as e:
        print(f"❌ An error occurred while writing detail data to CSV: {e}")


def append_skipped_to_csv(skipped_list, filename):
    """Appends failed links (ID and URL) to the dedicated skipped file."""
    if not skipped_list: return
    
    skipped_field_names = ['ID', 'URL']
    skipped_df = pd.DataFrame(skipped_list, columns=skipped_field_names)
    
    # Check if file exists to determine if header is needed
    write_header = not os.path.exists(filename) or os.path.getsize(filename) == 0
    
    try:
        skipped_df.to_csv(
            filename, 
            sep='|', 
            index=False, 
            mode='a', # <<< APPEND MODE
            header=write_header, # Write header only if file is new/empty
            quoting=csv.QUOTE_NONE,
            encoding='utf-8'
        )
        print(f"✅ Appended {len(skipped_list)} skipped links to **{filename}**")
    except Exception as e:
        print(f"❌ Error appending skipped links to CSV: {e}")
        
        # --- Main Orchestration Execution ---

if __name__ == "__main__":
    
    print(f"--- Starting Detail Scraping Orchestration ---")
    links_to_scrape = read_links_from_csv(INPUT_CSV_FILE)
    BATCH_SIZE = 1000
    BATCH_NUMBER = 13
    # START_INDEX = (BATCH_NUMBER - 1) * BATCH_SIZE
    START_INDEX = 13000
    # END_INDEX = START_INDEX + BATCH_SIZE
    END_INDEX = 13088
    links_to_scrape_batch = links_to_scrape[START_INDEX:END_INDEX]
    
    print(f"Total links found: {len(links_to_scrape)}")
    print(f"Running Batch {BATCH_NUMBER}: Scraping IDs {links_to_scrape_batch[0]['ID']} to {links_to_scrape_batch[-1]['ID']}")
    
    if not links_to_scrape_batch:
        print(f"⚠️ Batch {BATCH_NUMBER} is empty (Index {START_INDEX} is out of bounds). Exiting.")
        exit()
    
    links_to_scrape = links_to_scrape_batch
    
    # if LIMIT_DETAIL_SCRAPE is not None and links_to_scrape:
    #     links_to_scrape = links_to_scrape[:LIMIT_DETAIL_SCRAPE]
    #     print(f"Limiting detail scraping to the first {len(links_to_scrape)} links for verification.")

    if links_to_scrape:
        print(f"\n--- Scraping {len(links_to_scrape)} novel details ---")
        
        novel_data_list = []
        skipped_links_list = [] # List to collect skipped links
        detail_driver = initialize_uc_driver(headless=HEADLESS_MODE)
        
        if detail_driver:
            try:
                for i, link_data in enumerate(links_to_scrape):
                    link_id = link_data['ID']
                    link_url = link_data['URL']
                    
                    print(f"[{i+1}/{len(links_to_scrape)}] Scraping ID {link_id}: {link_url}")
                    
                    details = scrape_novel_details(link_url, detail_driver)
                    
                    if details and details.get('NAME') and (details['NAME'] != 'N/A'):
                        final_entry = {'ID': link_id, **details}
                        novel_data_list.append(final_entry)
                    else:
                        # --- LOGGING SKIPPED LINK ---
                        skipped_links_list.append({'ID': link_id, 'URL': link_url})
                        print(f"    Skipping ID {link_id}: Detail scraping failed or returned empty data.")
                        # ----------------------------
                    
                    time.sleep(1) # Delay between detail scrapes
            
            finally:
                if detail_driver:
                    try:
                        detail_driver.quit()
                    except Exception:
                        pass

        # 3. Write all collected data to the FINAL CSV files.
        write_details_to_csv(novel_data_list, OUTPUT_CSV_FILE, FIELD_NAMES)
        append_skipped_to_csv(skipped_links_list, SKIPPED_CSV_FILE) # <<< WRITE SKIPPED LIST

        # 4. Final Verification
        if novel_data_list:
            print("\n--- First Scraped Entry Verification ---")
            df_final = pd.DataFrame(novel_data_list)
            # Display only the first row
            try:
                print(df_final.head(1).to_markdown(index=False))
            except ImportError:
                 print(df_final.head(1).to_string(index=False))
    else:
        print("No valid links found or scraping yielded no data.")