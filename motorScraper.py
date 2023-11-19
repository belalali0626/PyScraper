import time

from selenium.common import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from browsermobproxy import Server

# Start BrowserMob Proxy server
server = Server()
server.start()
proxy = server.create_proxy()

# Set up Chrome WebDriver with proxy
option = webdriver.ChromeOptions()
proxy_url = proxy.proxy
proxy.add_to_capabilities(webdriver.DesiredCapabilities.CHROME.copy())

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

# Navigate to the website
url = 'https://www.motors.co.uk'
driver.get(url)

time.sleep(3)

search_postcode = driver.find_element(By.CSS_SELECTOR, 'input[id="searchPostcode"]')
search_make = driver.find_element(By.CSS_SELECTOR, 'select[aria-label="Select Make"]')
search_model = driver.find_element(By.CSS_SELECTOR, 'select[aria-label="Select Model"]')
find_btn = driver.find_element(By.CSS_SELECTOR, 'button[class="btn btn--expand sp__btn btn--spinner"]')

# Create Option Objects
select_make = Select(search_make)
select_model = Select(search_model)

# Perform Action
time.sleep(3)
search_postcode.send_keys("NW101PQ")
time.sleep(6)
select_make.select_by_value("BMW")
time.sleep(3)
select_model.select_by_value("1 Series")
time.sleep(5)
find_btn.click()

# Wait for search to be complete
time.sleep(10)

# Variable Setup
current_page = 1
total_pages = 2
wait = WebDriverWait(driver, 10)

# Data Scraping Logic
while current_page <= total_pages:
    try:
        car_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.sc-fbKhjd.jxKUBR')))

        for car_element in car_elements:
            try:
                car_name_element = WebDriverWait(car_element, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h3[class="title-4 no-margin"]'))
                )
                car_name_element_text = car_name_element.text.strip()
                print(car_name_element_text)

            except TimeoutException:
                print("Timeout waiting for car name element")

    except TimeoutException:
        print("Timeout waiting for car elements")

# You might want to navigate to the next page here, if applicable

# Stop BrowserMob Proxy server
server.stop()

driver.quit()
