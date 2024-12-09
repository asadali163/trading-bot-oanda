from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor

# WebDriver setup
def setup_driver(driver_path):
    service = Service(driver_path)
    return webdriver.Chrome(service=service)

# Generate URLs for a given year and month
def generate_urls(years, months):
    base_url = "https://www.forexfactory.com/calendar?month="
    urls = []
    for year in years:
        for month in months:
            urls.append(f"{base_url}{month.lower()}.{year}")
    return urls

# Scroll to the end of the page to load all data
def scroll_to_end(driver):
    while True:
        current_scroll = driver.execute_script("return window.scrollY + window.innerHeight;")
        total_height = driver.execute_script("return document.body.scrollHeight;")
        if current_scroll + 10 >= total_height:
            print("Reached the end of the page.")
            break
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(2)

# Extract rows from the table
def extract_rows(driver, url):
    year = url[-4:]
    data = []
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "calendar__table"))
    )
    table = driver.find_element(By.CLASS_NAME, "calendar__table")
    tbodies = table.find_elements(By.TAG_NAME, 'tbody')

    for tbody in tbodies:
        rows = tbody.find_element(By.CSS_SELECTOR, ".calendar__row.calendar__row--day-breaker")
        cell = rows.find_element(By.CLASS_NAME, "calendar__cell")
        date_cell = cell.find_element(By.TAG_NAME, 'span')
        date = f"{cell.get_attribute('innerHTML').split(' ')[0]} - {date_cell.get_attribute('innerHTML').strip()}"
        curr_date = date

        rows = tbody.find_elements(By.TAG_NAME, 'tr')[1:]
        prev_time = ''
        for row in rows:
            td_cells = row.find_elements(By.TAG_NAME, "td")
            curr_cell_data = {'date': f"{date} - {year}"}
            for td in td_cells:
                if "calendar__time" in td.get_attribute("class"):
                    time_divs = td.find_elements(By.TAG_NAME, 'div')
                    if time_divs and time_divs[0].text.strip():
                        prev_time = time_divs[0].text.strip()
                    curr_cell_data['time'] = prev_time
                elif "calendar__currency" in td.get_attribute("class"):
                    curr_cell_data['currency'] = td.text.strip() or "No currency available"
                elif "calendar__impact" in td.get_attribute("class"):
                    span = td.find_element(By.TAG_NAME, "span")
                    curr_cell_data['impact'] = span.get_attribute("title").split(' ')[0] if span else "No impact available"
                elif "calendar__event" in td.get_attribute("class"):
                    curr_cell_data['event'] = td.text.strip() or "No event available"
                elif "calendar__actual" in td.get_attribute("class"):
                    curr_cell_data['actual_value'] = td.text.strip() or np.nan
                elif "calendar__forecast" in td.get_attribute("class"):
                    curr_cell_data['forecast_value'] = td.text.strip() or np.nan
                elif "calendar__previous" in td.get_attribute("class"):
                    curr_cell_data['prev_value'] = td.text.strip() or np.nan
            data.append(curr_cell_data)
            print(curr_cell_data)
    return data

# Scrape a single URL
def scrape_url(url, driver_path):
    driver = setup_driver(driver_path)
    try:
        print(f"Scraping URL: {url}")
        driver.get(url)
        scroll_to_end(driver)
        data = extract_rows(driver, url)
        print(f"Completed scraping URL: {url}")
        return pd.DataFrame(data)
    finally:
        driver.quit()

# Save data to an Excel file
def save_to_excel(dataframes, filename):
    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

# Main function
def main():
    driver_path = r"C:\windows\webdriver\chromedriver.exe"  # Update with your path
    # urls = ['https://www.forexfactory.com/calendar?week=last',
    #         'https://www.forexfactory.com/calendar?week=this']

    years = [2023]
    months = [
        "November", "December"
    ]

    urls = generate_urls(years, months)
    

    # Use ThreadPoolExecutor for parallel scraping
    dataframes = []

    is_save = False
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(scrape_url, url, driver_path) for url in urls]
            for future in futures:
                dataframes.append(future.result())
    except Exception as e:
        save_to_excel(dataframes, f"../forex_calendar_data_{years[0]}.xlsx")
        is_save = True

    # Save all dataframes to an Excel file
    if not is_save:
        save_to_excel(dataframes, f"../forex_calendar_data_2023_remaining.xlsx")

if __name__ == "__main__":
    # main()
    pass
