import csv
import re
from playwright.sync_api import sync_playwright
import time
from fspy import FlareSolverr
from ProxyManager import get_next_proxy, mark_used


def wait_for_element(page, selector, timeout=5000):
    try:
        element_handle = page.wait_for_selector(selector, timeout=timeout)
        return element_handle
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Element with selector '{selector}' not found within the specified timeout.")
        return None


def extract_element_text(page, selector, timeout=5000):
    try:
        # Use page.$ to find the element
        element_handle = page.wait_for_selector(selector, timeout=timeout)

        # Check if the element is found
        if element_handle:
            # Use page.evaluate to extract the text content
            element_text = page.evaluate('(element) => element.textContent', element_handle)
            return element_text
        else:
            print(f"Element with selector '{selector}' not found within the specified timeout.")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def search_in_iframe(page, iframe_selector, selector_to_wait_for, button, button_selector, timeout=5000):
    try:
        iframe_handle = wait_for_element(page, iframe_selector, timeout=15000)

        if iframe_handle:
            iframe = iframe_handle.content_frame()
            iframe.wait_for_load_state()

            # Wait for a specific element within the iframe
            element_handle = iframe.wait_for_selector(selector_to_wait_for, timeout=timeout)

            if element_handle and button:
                print(f"Cookies text '{selector_to_wait_for}' found in the iframe.")
                print(f"Button '{button_selector}' is being clicked")

                click_button(iframe, button_selector, timeout)
                # Introduce a delay after clicking the button
                time.sleep(2)
            elif element_handle:
                print(f"Cookies text '{selector_to_wait_for}' found in the iframe.")
                return True

        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Cookies text '{selector_to_wait_for}' not found in the iframe within the specified timeout.")
        return False


def click_button(target, button_selector, timeout):
    button = target.wait_for_selector(button_selector, timeout=timeout)

    if button:
        print(f"Button '{button_selector}' found.")
        if button.is_enabled():
            button.click()
            print(f"Button '{button_selector}' clicked.")
            return True
        else:
            print(f"Button '{button_selector}' is not enabled.")
            return False
    else:
        print(f"Button '{button_selector}' not found.")
        return False


def extract_listing_details(listing_element):
    title = listing_element.eval_on_selector('h3', 'el => el.textContent')
    subtitle = listing_element.eval_on_selector('p[data-testid="search-listing-subtitle"]', 'el => el.textContent')

    # Add waiting logic for the price element
    price = wait_for_selector_content(listing_element, 'div.sc-gvZAcH p.sc-iGgWBj span.sc-bVVIoq', timeout=5000)

    mileage = listing_element.eval_on_selector('span[data-testid="search-listing-seller-mileage"]',
                                               'el => el.textContent')
    year = listing_element.eval_on_selector('span[data-testid="search-listing-seller-reg"]', 'el => el.textContent')

    # Extract the listing URL
    raw_url = listing_element.query_selector('a[data-testid="search-listing-title"]').get_attribute('href')

    # Extract the transmission
    transmission = wait_for_selector_content(listing_element, 'ul.sc-eBHhsj.fPmFbb li:nth-child(6)')

    # Extract the fuel type
    fuel_type = wait_for_selector_content(listing_element, 'ul.sc-eBHhsj.fPmFbb li:nth-child(7)')

    # Process values before adding to the dictionary
    mileage = mileage.replace('Mileage', '').strip() if mileage else None
    year = year.replace('Year and plate', '').strip() if year else None

    # Clean up the URL
    base_url = 'https://www.autotrader.co.uk'
    cleaned_url = f"{base_url}{raw_url.split('?')[0]}"

    # Extract the location text content
    location_element = listing_element.query_selector('.sc-knuQbY.iPnnQt')
    location = location_element.text_content() if location_element else None
    location = location.replace('Dealer location', '').strip() if location else None

    # Create a dictionary with the extracted details
    listing_details = {
        'url': cleaned_url,
        'title': title,
        'subtitle': subtitle,
        'price': price,
        'mileage': mileage,
        'year': year,
        'location': location,
        'transmission': transmission,
        'fuel_type': fuel_type,
    }

    return listing_details


def wait_for_selector_content(page, selector, timeout=5000):
    element_handle = None
    try:
        element_handle = page.wait_for_selector(selector, timeout=timeout)
        content = element_handle.text_content()
        return content.strip() if content else None
    except Exception as e:
        print(f"Error waiting for selector '{selector}': {e}")
    finally:
        if element_handle:
            element_handle.dispose()
    return None



def write_to_csv(data, filename='car_listings_text.csv'):
    with open(filename, mode='a+', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Check if the file is empty and write headers
        if file.tell() == 0:
            header = data[0].keys()
            writer.writerow(header)

        # Write data to the CSV file
        for row in data:
            writer.writerow(row.values())


def create_flare_instance(url, proxy="None", increment="None", max_retries=5):
    solver = FlareSolverr()

    for retry_count in range(max_retries + 1):
        try:
            if proxy is None:
                session_id = solver.create_session()
            else:
                session_id = solver.create_session(increment, proxy)

            response = solver.request_get(url)

            if response.status == "ok":
                print(f"Request to {url} was successful, Status code: {response.status}")
                return response
            else:
                print(f"Request to {url} was not successful. Status code: {response.status}")
                return None

        except Exception as e:
            print(f"Error handling Cloudflare challenge: {e} - Trying new proxy")
            proxy = get_next_proxy()

    return None


def main():
    with sync_playwright() as p:
        new_proxy = get_next_proxy()
        increment_value = 1
        # Browser setup
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Selectors
        iframe_selector = 'iframe[title="SP Consent Message"]'
        cookies_text = 'p.message-component'
        accept_button = 'div.message-row button[title="Accept All"]'
        page_element = 'p[data-testid="pagination-show"]'
        next_button = 'a[data-testid="pagination-next"]'

        # Load up the page
        page_url = 'https://www.autotrader.co.uk/car-search?postcode=NW1%209PQ&year-to=2023&make=BMW&model=1%20Series' \
                   '&advertising-location=at_cars&page=1'

        # Handle Cloudflare challenges
        handled_response_content = create_flare_instance(page_url, new_proxy, f"Instance: {increment_value}")

        if handled_response_content is not None:
            # Continue with your existing script

            # Load up the page
            page.goto(page_url, timeout=50000)

            # wait for the iframe, then look for the cookies text within iframe, then the parameters
            search_in_iframe(page, iframe_selector, cookies_text, True, accept_button, timeout=15000)

            # find cars
            page.wait_for_selector('section[data-testid="trader-seller-listing"]')

            # find page
            page_extract = extract_element_text(page, page_element)
            page_number = int(re.search(r'\b\d+\b', page_extract[::-1]).group()[::-1]) if page_extract and re.search(
                r'\b\d+\b', page_extract) else None

            all_listing_details = []

            # Extract details from each listing on the page
            for current_page in range(page_number):
                listings = page.query_selector_all('section[data-testid="trader-seller-listing"]')

                for idx, listing in enumerate(listings, start=1):
                    details = extract_listing_details(listing)
                    all_listing_details.append(details)

                click_button(page, next_button, 5000)
                wait_for_element(page, 'section[data-testid="trader-seller-listing"]', 5000)

                print(f'Current Page is : {current_page}')

                # Write the data to CSV incrementally (e.g., every 10 pages)
                if current_page % 10 == 0:
                    write_to_csv(all_listing_details)
                    all_listing_details = []  # clear the list for the next batch

                if current_page % 30 == 0:
                    new_proxy = get_next_proxy()

                    if new_proxy:
                        # Close the existing context
                        context.close()

                        context.close()
                        context = browser.new_context(proxy={'server': new_proxy})
                        page = context.new_page()

            browser.close()


if __name__ == "__main__":
    main()