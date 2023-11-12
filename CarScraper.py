from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

option = webdriver.ChromeOptions()
option.add_argument("start-maximized")


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)

driver.get('https://www.autotrader.co.uk/car-search?postcode=nw23sn&year-to=2023&make=Ford&include-delivery-option=on&advertising-location=at_cars&page=1')

wait = WebDriverWait(driver, 10)  # You can adjust the timeout as needed

carCard = driver.find_elements(By.XPATH, '//*[@class="sc-fbKhjd jxKUBR"]')

for car in carCard:
    #model = car.find_elements(By.XPATH,'//a[@data-testid="search-listing-title"]/h3')
    #car_names = [element.find_elements(By.TAG_NAME,'h3').text for element in model]
    elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[@data-testid='search-listing-title']/h3")))
    price_element = driver.find_element(By.XPATH, '//span[@class="sc-ePDLzJ gfdAKZ"]')
    # Extract car names from the elements
    car_names = set(element.text for element in elements if element.text.strip())
    price_text = price_element.text

    print(car_names)
    print(price_text)


driver.quit()
