import csv
import re
import time
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

option = webdriver.ChromeOptions()
option.add_argument("start-maximized")
option.add_argument("--disable-notifications")  # Example option to disable notifications


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

driver.get(
    'https://www.autotrader.co.uk/car-search?advertising-location=at_cars&include-delivery-option=on&make=BMW&model=1%20Series&postcode=NW1%209PQ&year-to=2023')

# Wait for the 'Accept All' button to be clickable
try:
    # Wait for the container to be present
    div_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'html[lang="en"].sp-message-open'))
    )

    # Wait for the main iframe to be present
    main_iframe_locator = (By.ID, 'sp_message_iframe_939601')
    WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(main_iframe_locator))

    # Wait for the "Accept All" button to be present and clickable
    accept_all_button_locator = (By.XPATH, '//button[@title="Accept All" and @aria-label="Accept All"]')
    accept_all_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(accept_all_button_locator))
    # Click the "Accept All" button
    accept_all_button.click()
    print("Accepted cookies.")

    # Switch back to the default content
    driver.switch_to.default_content()

    time.sleep(4)
except (TimeoutException, NoSuchElementException):
    print("No 'Accept All' button found or not clickable. Proceeding without accepting.")
    driver.quit()
    raise


# Wait for at least one car element to be present
wait = WebDriverWait(driver, 10)

total_pages_element = driver.find_element(By.CSS_SELECTOR, 'p[data-testid="pagination-show"].sc-jXbUNg.fJiHvq')
total_pages_text = total_pages_element.text.strip()

# Use regular expression to extract the number
match = re.search(r'Page \d+ of (\d+)', total_pages_text)
total_pages = int(match.group(1))

current_page = 1
i = 1  # Move the counter outside the loop

# Create a new CSV file and write the header
csv_file_path = '../car_details.csv'
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Id', 'Name', 'Mileage', 'Year', 'Price', 'URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    while current_page <= total_pages:
        try:
            # Wait for at least one car element to be present
            car_elements = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'sc-fbKhjd.KtDDQ')))
            car_cards = []

            for car_element in car_elements:
                try:
                    # Wait for the car name element to be present within the car element
                    car_name_element = WebDriverWait(car_element, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.sc-dlWCHZ li:nth-child(3)'))
                    )
                    car_name = car_name_element.text.strip()

                    # Find Mileage Element
                    mileage_element = car_element.find_element(By.CSS_SELECTOR, 'ul.sc-dlWCHZ li:nth-child(3)')
                    mileage = mileage_element.text.strip()

                    # Find Year Element
                    year_element = car_element.find_element(By.CSS_SELECTOR, 'ul.sc-dlWCHZ li:nth-child(1)')
                    year = year_element.text.strip()

                    # Find Price Element
                    price_element = car_element.find_element(By.CSS_SELECTOR,
                                                             'section.sc-gvZAcH p.sc-iGgWBj span.sc-bVVIoq')
                    price = price_element.text.strip()

                    # Find Link Element
                    link_element = car_element.find_element(By.CSS_SELECTOR, 'a[data-testid="search-listing-title"]')
                    listing_url = link_element.get_attribute('href')
                    listing = link_element.get_attribute('href').strip()

                    # Check if the car name is not empty before appending to the list
                    if car_name:
                        car_cards.append({
                            'Id': i,
                            'Name': car_name,
                            'Mileage': mileage,
                            'Year': year,
                            'Price': price,
                            'URL': listing
                        })
                        print(f"Car {i} details retrieved successfully.")
                        i += 1  # Increment the counter
                    else:
                        print(f"Car {i}: Empty car name")
                except Exception as e:
                    print(f"Error extracting details for Car {i}: {e}")

            # Write the car details to the CSV file
            with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                for car_card in car_cards:
                    writer.writerow(car_card)

            for car_card in car_cards:
                print(f"Car {car_card['Id']}:")
                for key, value in car_card.items():
                    print(f"   {key}: {value}")
                print()  # Add a newline between entries

            # Increment the current page counter
            current_page += 1

            # Navigate to the next page
            if current_page <= total_pages:
                next_page_url = f'https://www.autotrader.co.uk/car-search?advertising-location=at_cars&include-delivery' \
                                f'-option=on&make=BMW&model=1%20Series&postcode=NW1%209PQ&year-to=2023&page={current_page}'
                driver.get(next_page_url)

                # Wait for the specific iframe
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'lpSS_68456113145')))

        except TimeoutException:
            print(f"Timeout waiting for car elements on page {current_page}. Proceeding to the next page.")

# Close the browser after the loop completes
driver.quit()
