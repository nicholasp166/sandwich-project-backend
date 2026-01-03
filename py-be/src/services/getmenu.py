import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import json
from playwright.sync_api import sync_playwright
import time

class PublixSubFetcher:
    def __init__(self, url):
        self.url = url

    def confirm_search(self): 
        #confirm we're actually on the deli page
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            search_header = soup.find('div', class_='search-page-header-container')
            #print(search_header)
            if search_header:
                bc = soup.find('search-browse-page-header')
                breadcrumbs = bc.get(':structured-breadcrumbs')
                #breadcrumbs = soup.find('search-browse-page-header')
                #print(json.loads(breadcrumbs))
                if breadcrumbs:
                    try:
                        pb = json.loads(breadcrumbs)
                       # print(json.dumps(pb, indent=2))
                        for item in pb:
                            if item["Name"] == "Deli Subs":
                                return True

                        return pb
                    except json.JSONDecodeError as e:
                        print("Error decoding JSON:", e)
            else:
                print("Search header not found.")  
            return False        
        except requests.exceptions.RequestException as e:
            print(f"Error confirming search URL: {e}")
            return False

    def get_menu_items(self):
        #get the sandwiches
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            search_header = soup.find('div', class_='search-results-super-container')
            if search_header:
                bc = search_header.find('div',class_="search-content-column").find('div', class_="p-grid-item")
                print(bc)
                for child in search_header.children:
                    if isinstance(child,Tag):
                        pass#print(child)
            else:
                print("Nothing")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")
            return False
        
    def get_menu_items_playwright(self, pagination=False):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(self.url)

                page.wait_for_selector('div.search-content-column')
                search_content_locators = page.locator('div.p-grid-item[data-qa-automation="p-card"]').all()
                card_list_htmls = {}

                if search_content_locators:
                    print(f"Found {len(search_content_locators)} elements with 'div.card-list'.")
                    for i, element_locator in enumerate(search_content_locators):
                        target_scroll_height = page.evaluate('document.body.scrollHeight')
                        current_scroll_position = page.evaluate('window.scrollY')
                        
                        # Define parameters for the slow scroll
                        scroll_duration_seconds = 1.0  # Total time for the scroll
                        scroll_steps = 10              # Number of intermediate scroll steps
                        
                        if target_scroll_height > current_scroll_position:
                            scroll_increment = (target_scroll_height - current_scroll_position) / scroll_steps
                            time_per_step = scroll_duration_seconds / scroll_steps
                            
                            for step in range(1, scroll_steps + 1):
                                next_scroll_position = current_scroll_position + (scroll_increment * step)
                                page.evaluate(f'window.scrollTo(0, {next_scroll_position})')
                                time.sleep(time_per_step)

                        content_wrapper_locator = element_locator.locator('div.content-wrapper')   
                        # Get the inner HTML content as a string from the content_wrapper
                        html_content = content_wrapper_locator.locator('div.top-section div.title-wrapper').inner_html()
                        item_soup = BeautifulSoup(html_content, 'html.parser')
                        #print(f"HTML content of item {i}:\n{html_content}\n")
                        first_link_tag = item_soup.find('a') 
                        
                        if first_link_tag:
                            # Get all text content from the <a> element
                            link_text = first_link_tag.get_text(strip=True) # Added strip=True for cleaner text
                            print(f"Text from link Pos {i}: {link_text}")
                            card_list_htmls[i] = link_text
                        else:
                            print("No <a> element found in this item's HTML.")       
                        time.sleep(1)
                    print(f"Total items in 'card_list_htmls': {len(card_list_htmls)}")
                else:
                    print("No 'div.card-list' elements found.")

                browser.close()
            return card_list_htmls # Return the list of HTML strings
        except Exception as e:
            print(f"Error using Playwright: {e}")
            return False

if __name__ == "__main__":
    url = "https://www.publix.com/c/deli-subs/33957951-95fa-4408-b54a-dd570a7e8648"  # Example URL
    fetcher = PublixSubFetcher(url)
    try:
        breadcrumbs = fetcher.confirm_search()
        print(breadcrumbs)
        if breadcrumbs == False:
            fetcher.get_menu_items()
        fetcher.get_menu_items_playwright()

    except Exception as e:
        print(f"Error occurred: {e}")