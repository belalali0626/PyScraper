import concurrent
from concurrent import futures
import time
import re
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def extract_year_info(carname):
    match = re.search(r'(\d{4} \(\d{2}\))', carname)
    return match.group(1) if match else None


def get_car_name(car_element):
    return WebDriverWait(car_element, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'h3[class="title-4 no-margin"]'))).text.strip()


def get_mileage(car_element):
    return car_element.find_element(By.CSS_SELECTOR,
                                    'li.flex.flex-column.j-space-between.a-center:nth-child(2)').text.strip()


def get_price(car_element):
    try:
        # Locate the div with class 'title-3'
        price_element = car_element.find_element(By.CSS_SELECTOR, 'div.title-3.no-scale.no-margin')

        # Return the text of the element
        price_text = price_element.text.strip()

        # Use regular expression to extract the price value
        price_match = re.search(r'£([\d,]+)', price_text)

        if price_match:
            price_value = price_match.group(1)
            return price_value
        else:
            print(f"Price not found in element text: {price_text}")
            return None

    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        return None

    except TimeoutException as e:
        print(f"Timeout waiting for element: {e}")
        return None

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        return None

    except TimeoutException as e:
        print(f"Timeout waiting for element: {e}")
        return None

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def get_listing_url(driver, car_element):
    result_card_footer = driver.find_element(By.CSS_SELECTOR, 'div.result-card__footer.flex.a-center.j-space-between')
    link_element = result_card_footer.find_element(By.CSS_SELECTOR, 'a')
    relative_link = link_element.get_attribute('href')
    return 'https://www.motors.co.uk' + relative_link


def get_engine(car_element):
    try:
        # Corrected XPath expression using position() function
        return car_element.find_element(By.XPATH,
                                        '//li[@class="flex flex-column j-space-between a-center"][1]').text.strip()

    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        return None

    except TimeoutException as e:
        print(f"Timeout waiting for element: {e}")
        return None


def get_fuel(car_element):
    try:
        # Corrected XPath expression using position() function
        return car_element.find_element(By.XPATH,
                                        '//li[@class="flex flex-column j-space-between a-center"][3]').text.strip()

    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        return None

    except TimeoutException as e:
        print(f"Timeout waiting for element: {e}")
        return None


def get_transmission(car_element):
    try:
        # Corrected XPath expression using position() function
        return car_element.find_element(By.XPATH,
                                        '//li[@class="flex flex-column j-space-between a-center"][4]').text.strip()

    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        return None

    except TimeoutException as e:
        print(f"Timeout waiting for element: {e}")
        return None
def extract_number_from_string(input_string):
    # Use regex to extract the number and remove spaces
    match = re.search(r'(\d+)', input_string)
    result = match.group(1) if match else None
    result_without_spaces = result.replace(" ", "") if result else None
    return result_without_spaces

# Example usage in a function
def extract_page_number(page_info):
    return extract_number_from_string(page_info)

def check_current_page(current_page_no):
    button_locator = (By.XPATH, '//button[@class="pgn__link btn active"]')
    active_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located(button_locator))

    # Extract the page number from the button
    button_text = active_button.text.strip()
    button_page_number = int(button_text) if button_text.isdigit() else None

    # Check if the extracted page number matches the current page number
    if button_page_number is not None and button_page_number == current_page_no:
        print(f"The current page is {current_page_no}")
        return True
    else:
        print(f"The current page is not {current_page_no}")
        return False


options = webdriver.ChromeOptions()
# Set the user agent to simulate a real-like browser
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/58.0.3029.110 Safari/537.3")
options.add_argument("blink-settings=imagesEnabled=true")
options.add_argument("--disable-infobars")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("window-size=1366,768")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--enable-features=NetworkServiceInProcess")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Navigate to the website
url = 'https://www.motors.co.uk'
driver.get(url)

time.sleep(3)
# Set-up Path to CSV
csv_file_path = 'car_details.csv'

# Find Input Fields
search_postcode = driver.find_element(By.CSS_SELECTOR, 'input[id="searchPostcode"]')
search_make = driver.find_element(By.CSS_SELECTOR, 'select[aria-label="Select Make"]')
search_model = driver.find_element(By.CSS_SELECTOR, 'select[aria-label="Select Model"]')
find_btn = driver.find_element(By.CSS_SELECTOR, 'button[class="btn btn--expand sp__btn btn--spinner"]')

# Create Option Objects
select_make = Select(search_make)
select_model = Select(search_model)

# Perform Action
search_postcode.send_keys("NW101PQ")
select_make.select_by_value("BMW")
select_model.select_by_value("1 Series")
time.sleep(3)
find_btn.click()

# Wait for search to be complete
time.sleep(10)

# Variable Setup
current_page = 1
isCurrent = False
wait = WebDriverWait(driver, 10)
total_pages = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[class="pgn__text"]')))
total_pages_text = total_pages.text.strip()
page_number = int(extract_page_number(total_pages_text))

i = 1  # Move the counter outside the loop

# Data Scraping Logic
car_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="result-card  "]')))
car_cards = []


# Function to scrape car details
def scrape_car_details(car_element):
    try:
        car_name = get_car_name(car_element)
        mileage = get_mileage(car_element)
        year = extract_year_info(car_name)
        price = get_price(car_element)
        listing = get_listing_url(driver, car_element)
        engine = get_engine(car_element)
        fuel = get_fuel(car_element)
        transmission = get_transmission(car_element)

        # Check if the car name is not empty before appending to the list
        if car_name:
            car_details = {
                'Id': i,
                'Name': car_name,
                'Mileage': mileage,
                'Year': year,
                'Price': price,
                'URL': listing,
                'Engine': engine,
                'Fuel': fuel,
                'Transmission': transmission
            }

            # Print the details for the current car
            print(f"Car {i} details:")
            for key, value in car_details.items():
                print(f"{key}: {value}")

            print(f"Car {i} details retrieved successfully.")
            return car_details

    except TimeoutException as te:
        print(f"Timeout waiting for car name element in child_element: {te}")
    return None


with concurrent.futures.ThreadPoolExecutor() as executor:
    while current_page <= page_number:
        # Submit tasks for each car_element
        futures = [executor.submit(scrape_car_details, car_element) for car_element in car_elements]
        # Collect results as they complete
        for future in concurrent.futures.as_completed(futures):
            car_details_result = future.result()
            if car_details_result:
                car_cards.append(car_details_result)
                i += 1  # Increment the counter
        # Navigate to the next page
        if current_page <= page_number:
            # Wait for the button to be clickable
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'pgn__next'))
            )
    # Click the button
            next_button.click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[class="pgn__text"]')))
            current_page += 1
            time.sleep(10)
            if check_current_page(current_page):
                print('same page')
                pass

# Clean up
driver.quit()
