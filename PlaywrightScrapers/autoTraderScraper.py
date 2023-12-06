import time
from playwright.sync_api import sync_playwright


def wait_for_element(page, selector, timeout=5000):
    try:
        element_handle = page.wait_for_selector(selector, timeout=timeout)
        return element_handle
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Element with selector '{selector}' not found within the specified timeout.")
        return None


def search_in_iframe(page, iframe_selector, selector_to_wait_for,button, button_selector, timeout=5000):
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

with sync_playwright() as p:
    # Browser setup
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Selectors
    iframe_selector = 'iframe[title="SP Consent Message"]'
    cookies_text = 'p.message-component'
    accept_button = 'div.message-row button[title="Accept All"]'

    # Load up the page
    page.goto(
        'https://www.autotrader.co.uk/car-search?advertising-location=at_cars&include-delivery-option=on&make=BMW'
        '&model=1%20Series&postcode=NW1%209PQ&year-to=2023')

    # wait for the iframe, then look for the cookies text within iframe
    search_in_iframe(page, iframe_selector, cookies_text,True, accept_button, timeout=15000)


    time.sleep(50)

    # Close the browser
    browser.close()
