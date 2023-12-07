import re
from playwright.sync_api import sync_playwright
import time


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


with sync_playwright() as p:
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
    page.goto(
        'https://www.autotrader.co.uk/car-search?postcode=NW1%209PQ&year-to=2023&make=BMW&model=1%20Series'
        '&advertising-location=at_cars&page=1')

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
            print('done all')

        click_button(page, next_button, 5000)
        wait_for_element(page, 'section[data-testid="trader-seller-listing"]', 5000)

    for idx, details in enumerate(all_listing_details, start=1):
        print(f"Listing {idx} Details:")
        print(f"Title: {details['title']}")
        print(f"Subtitle: {details['subtitle']}")
        print(f"Price: {details['price']}")
        print(f"Mileage: {details['mileage']}")
        print(f"Year: {details['year']}")
        print(f"Location: {details['location']}")
        print(f"URL: {details['url']}")
        print("\n")

    browser.close()
