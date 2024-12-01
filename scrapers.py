from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
import time

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

    # print("Total days are: ", len(tbodies))
    
    for tbody in tbodies:
            rows = tbody.find_element(By.CSS_SELECTOR, ".calendar__row.calendar__row--day-breaker")
            cell = rows.find_element(By.CLASS_NAME, "calendar__cell")
            date_cell = cell.find_element(By.TAG_NAME, 'span')
            date = f"{cell.get_attribute('innerHTML').split(' ')[0]} - {date_cell.get_attribute('innerHTML').strip()}"
            print("Date: ", date)
            curr_date = date

            # Get the event rows
            rows = tbody.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip the first row
            prev_time = ''
            for row in rows:
                td_cells = row.find_elements(By.TAG_NAME, "td")
                # print("LEN: ", len(td_cells))
                
                curr_cell_data = dict()
                curr_cell_data['date'] = f"{date} - {year}"

                for td in td_cells:
                    if "calendar__time" in td.get_attribute("class"):
                        time_divs = td.find_elements(By.TAG_NAME, 'div')  # Returns a list of elements
                        if time_divs:  # If a <div> exists
                            time_div = time_divs[0]  # Get the first <div>
                            
                            # Check if a <span> exists in the <div>
                            time_spans = time_div.find_elements(By.TAG_NAME, 'span')
                            if time_spans:  # If a <span> exists
                                time_span = time_spans[0]  # Get the first <span>
                                if time_span.text.strip():
                                    time_text = time_span.text.strip()
                                    prev_time = time_text
                                    # print("Previous time: ", prev_time)
                                else:
                                    time_text = prev_time
                        else:
                            time_text = prev_time
                        curr_cell_data['time'] = time_text

                    if "calendar__currency" in td.get_attribute("class"):
                        currency_text = td.text.strip() if td.text.strip() else "No currency available"
                        # print(f"Currency: {currency_text}")
                        curr_cell_data['currency'] = currency_text


                    if "calendar__impact" in td.get_attribute("class"):
                        span = td.find_element(By.TAG_NAME, "span")
                        impact_title = span.get_attribute("title").strip() if span.get_attribute("title") else "No impact available"
                        # print(f"Impact: {impact_title}")
                        curr_cell_data['impact'] = impact_title.split(' ')[0]

                    if "calendar__event" in td.get_attribute("class"):
                        event_text = td.text.strip() if td.text.strip() else "No event available"
                        # print(f"Event: {event_text}")
                        curr_cell_data['event'] = event_text

                    if "calendar__actual" in td.get_attribute("class"):
                        actual_value = td.text.strip() if td.text.strip() else "No actual value available"
                        # print(f"Actual Value: {actual_value}")
                        if actual_value == 'No actual value available':
                            curr_cell_data['actual_value'] = np.nan
                        else:
                            curr_cell_data['actual_value'] = actual_value

                    if "calendar__forecast" in td.get_attribute("class"):
                        forecast_value = td.text.strip() if td.text.strip() else "No forecast value available"
                        # print(f"Forecast Value: {forecast_value}")
                        if forecast_value == "No forecast value available":
                            curr_cell_data['forecast_value'] = np.nan
                        else:
                            curr_cell_data['forecast_value'] = forecast_value

                    if "calendar__previous" in td.get_attribute("class"):
                        previous_value = td.text.strip() if td.text.strip() else "No previous value available"
                        # print(f"Previous Value: {previous_value}")
                        if previous_value == "No previous value available":
                            curr_cell_data['prev_value'] = np.nan
                        else:
                            curr_cell_data['prev_value'] = previous_value

                data.append(curr_cell_data)
                print(curr_cell_data)
                print("-" * 50)  # Separator for clarity
    
    return data

# Save data to an Excel file
def save_to_excel(dataframes, filename):
    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

# Main function
def main():
    # driver_path = r"C:\windows\webdriver\chromedriver.exe"  # Update with your path
    # driver = setup_driver(driver_path)
    
    years = [2020, 2021, 2022, 2023, 2024]
    months = [
        "January", "February", "March", "April", "May", 
        "June", "July", "August", "September", "October", 
        "November", "December"
    ]
    
    urls = generate_urls(years, months)
    dataframes = []
    # print(urls)

    # urls = ['https://www.forexfactory.com/calendar?week=last',
    #         'https://www.forexfactory.com/calendar?week=this']
    
    try:
        for url in urls:
            driver_path = r"C:\windows\webdriver\chromedriver.exe"  # Update with your path
            driver = setup_driver(driver_path)
            print(f"Scraping URL: {url}")
            driver.get(url)
            scroll_to_end(driver)
            data = extract_rows(driver, url)
            df = pd.DataFrame(data)
            dataframes.append(df)
            print("Apended into the dataframes list: ", len(dataframes))

        # Save all dataframes to an Excel file
        save_to_excel(dataframes, "../forex_calendar_data.xlsx")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
