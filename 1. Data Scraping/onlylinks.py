import csv
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml import etree
from io import StringIO
import time
import re
import os

# --- Global Configurations ---
DASHBOARD_URL = "https://Example.com/Book"
CSV_FILE_NAME = "links.csv"
FIELD_NAMES = ['ID', 'URL'] 
MAX_PAGES_TO_SCRAPE = 661 
# ------------------------------------------------------------

# XPaths for Dashboard Page (Link Collection)
DASHBOARD_XPATHS = {
    'NOVEL_LINKS_HREF': '//div[contains(@class, "list-novel")]//h3[@class="novel-title"]/a/@href',
    'NOVEL_LINK_WAIT': '//div[contains(@class, "list-novel")]//h3[@class="novel-title"]/a',
    'PAGINATION_BAR': '//ul[@class="pagination"]'
}

# --- Utility Functions ---

def initialize_uc_driver(headless=True):
    """Initializes and returns an undetected_chromedriver instance."""
    options = uc.ChromeOptions()
    if headless:
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu') 
        
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize undetected_chromedriver: {e}")
        return None

def get_lxml_tree(html_content):
    """Parses HTML content into an LXML tree for XPath querying."""
    parser = etree.HTMLParser()
    return etree.parse(StringIO(html_content), parser)

def collect_novel_links(base_url):
    """Navigates the dashboard pages and collects all unique novel links across all pages."""
    driver = initialize_uc_driver(headless=True)
    if not driver:
        return []

    all_novel_links = set()
    max_pages = MAX_PAGES_TO_SCRAPE 
    
    print(f"Starting link collection across {max_pages} page(s) (1 to {max_pages}).")

    # --- Iterate through all pages and collect links ---
    try:
        for page_num in range(1, max_pages + 1):
            url = f"{base_url}?page={page_num}"
            
            try:
                print(f"Attempting navigation to page {page_num}...")
                driver.get(url)
                
                # CRITICAL WAIT: Wait for a novel link element to confirm the page content loaded correctly
                # Using a 10s timeout, as a 5s wait plus 10s explicit wait should be sufficient.
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, DASHBOARD_XPATHS['NOVEL_LINK_WAIT']))
                )
                
                # Data Extraction
                tree = get_lxml_tree(driver.page_source)
                links_on_page = tree.xpath(DASHBOARD_XPATHS['NOVEL_LINKS_HREF'])
                
                if not links_on_page:
                    print(f"   ⚠️ Page {page_num} loaded, but zero links found. Check page for anti-bot blocks.")
                    continue

                # Process and update links
                full_links = [link if link.startswith('http') else f"https://Example.com{link}" for link in links_on_page]
                clean_links = [link.split('#')[0] for link in full_links]
                all_novel_links.update(clean_links)
                
                print(f"-> Page {page_num}/{max_pages}: Found {len(links_on_page)} links. Total unique links: {len(all_novel_links)}")
                time.sleep(1.5) # Be polite and wait between pages

            except Exception as e:
                # If a page fails to load, log the error and move to the next iteration
                print(f"   ❌ Error extracting links on page {page_num}. Skipping page. Error: {e}")
                time.sleep(3) # Longer wait before skipping to the next page
            
    finally:
        # Explicitly quit the driver once the loop completes or an unrecoverable error occurs
        if driver:
            try:
                driver.quit()
            except Exception as e:
                # Ignore the specific WinError 6 handle error
                print(f"Driver cleanup encountered an error (ignored): {e}")

        return list(all_novel_links)

def write_to_csv(link_list, filename):
    """Writes the list of novel links to a CSV file."""
    if not link_list:
        print("No links collected to write to CSV.")
        return

    # Prepare data with unique IDs
    data_for_csv = [{'ID': i + 1, 'URL': url} for i, url in enumerate(link_list)]

    try:
        link_field_names = ['ID', 'URL']
        # Use 'a' (append) mode if you want to keep previously scraped links across restarts, 
        # but 'w' (write) mode is safer for a complete, fresh scrape run.
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile: 
            writer = csv.DictWriter(csvfile, fieldnames=link_field_names, delimiter='|')
            
            writer.writeheader()
            writer.writerows(data_for_csv)
            
        print(f"\n✅ Successfully wrote {len(data_for_csv)} unique novel links to **{filename}**")
    except Exception as e:
        print(f"❌ An error occurred while writing to CSV: {e}")

# --- Main Execution ---

if __name__ == "__main__":
    print(f"--- Starting Novel Link Collection from {DASHBOARD_URL} ---")
    
    # STEP 1: Collect all unique novel links.
    novel_links = collect_novel_links(DASHBOARD_URL) 
    
    # STEP 2: Write all collected links to a CSV file.
    write_to_csv(novel_links, CSV_FILE_NAME)