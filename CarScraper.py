from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

option = webdriver.ChromeOptions()
option.add_argument("start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

driver.get('https://www.autotrader.co.uk/car-search?advertising-location=at_cars&include-delivery-option=on&make=Ford&postcode=nw110pu')

# Wait for the 'Accept All' button to be clickable
try:
    # Wait for the container to be present
    div_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, 'sp_message_container_908484'))
    )

    # Switch to the iframe
    iframe = div_element.find_element(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(iframe)

    # Find the "Accept All" button within the iframe
    accept_all_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@title="Accept All"]'))
    )

    # Click the "Accept All" button
    accept_all_button.click()

    # Switch back to the default content
    driver.switch_to.default_content()
    print("Terms and conditions accepted.")
except (TimeoutException, NoSuchElementException):
    print("No 'Accept All' button found or not clickable. Proceeding without accepting.")

# Wait for at least one car element to be present
wait = WebDriverWait(driver, 10)
car_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.sc-fbKhjd.jxKUBR')))

# Extract car names from each car element
car_cards = []
for i, car_element in enumerate(car_elements, start=1):
    try:
        # Wait for the car name element to be present within the car element
        car_name_element = WebDriverWait(car_element, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.sc-kAyceB h3'))
        )
        car_name = car_name_element.text.strip()

        mileage_element = car_element.find_element(By.CSS_SELECTOR, 'ul.sc-dPZUQH li:nth-child(3)')
        mileage = mileage_element.text.strip()

        year_element = car_element.find_element(By.CSS_SELECTOR, 'ul.sc-dPZUQH li:nth-child(1)')
        year = year_element.text.strip()

        price_element = car_element.find_element(By.CSS_SELECTOR,
                                                 'section.sc-kqGoIF div.sc-dxcDKg p.sc-iGgWBj span.sc-ePDLzJ')
        price = price_element.text.strip()

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
        else:
            print(f"Car {i}: Empty car name")
    except Exception as e:
        print(f"Error extracting details for Car {i}: {e}")

for car_card in car_cards:
    print(f"Car {car_card['Id']}:")
    for key, value in car_card.items():
        print(f"   {key}: {value}")
    print()  # Add a newline between entries

# Close the browser
driver.quit()
