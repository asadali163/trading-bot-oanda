from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = False  # Disable headless mode


# Set up the WebDriver
from selenium.webdriver.chrome.service import Service
driver_path = r"C:\windows\webdriver\chromedriver.exe"  # Update with your path
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

try:
    # 1. Navigate to the website
    driver.get("https://www.forexfactory.com/calendar")
    time.sleep(2)  # Wait for the page to load

    # 2. Locate the anchor tag with the class and click it
    date_range_element = driver.find_element(By.CLASS_NAME, "highlight.light.options")
    date_range_element.click()
    time.sleep(2)  # Wait for the date picker to appear

    # 3. Set the date range
    prev_year_button = driver.find_element(By.CLASS_NAME, "date-range-selector__button--prev-year")
    prev_month_button = driver.find_element(By.CLASS_NAME, "date-range-selector__button--prev-month")
    next_month_button = driver.find_element(By.CLASS_NAME, "date-range-selector__button--next-month")
    next_year_button = driver.find_element(By.CLASS_NAME, "date-range-selector__button--next-year")

    # Navigate to September 2024
    while True:
        header_element = driver.find_element(By.CSS_SELECTOR, "div.cal__header")
        header = header_element.get_attribute("innerHTML").strip()
        print("Header is:", header)
        
        if header == "June 2024":
            break
        
        prev_month_button.click()
        time.sleep(1)  # Wait for UI update

    # Select 15th September 2024
    desired_date = "15"
    date_elements = driver.find_elements(By.CLASS_NAME, "cal__day")
    for date_element in date_elements:
        if date_element.text == desired_date:
            date_element.click()
            break

    # Now navigate to October 2024
    while True:
        header_element = driver.find_element(By.CSS_SELECTOR, "div.cal__header")
        header = header_element.get_attribute("innerHTML").strip()
        print("Header is:", header)
        
        if header == "October 2024":
            break
        
        next_month_button.click()
        time.sleep(1)  # Wait for UI update

    # Select 15th October 2024
    desired_date = "15"
    date_elements = driver.find_elements(By.CLASS_NAME, "cal__day")
    for date_element in date_elements:
        if date_element.text == desired_date:
            date_element.click()
            break

    # Close the driver
    time.sleep(2)
    

    # 4. Click the "Apply settings" button
    apply_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".overlay__button.overlay__button--submit.button"))
    )
    driver.execute_script("arguments[0].click();", apply_button)
    print("Button Clicked here....")
    # WebDriverWait(driver, 20).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, ".calendar__events"))  # Adjust this selector
    # )

    time.sleep(100)
    print("Results have been loaded")
    print("Date range updated successfully!")

finally:
    # Close the browser
    driver.quit()
