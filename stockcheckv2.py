from selenium import webdriver
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time

def init_worker():
    global driver
    global main_tab
    options = Options()
    options.add_argument("--headless=new")  # run in headless mode
    options.add_argument("--log-level=3")  # suppress console logs
    driver = webdriver.Chrome(options=options)
    driver.get("about:blank")
    main_tab = driver.current_window_handle

def checkURLParallel(url):
    global driver
    global main_tab
    url += "buy"
    print(url)
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)

    try:
        WebDriverWait(driver, 2, ignored_exceptions=[TimeoutException]).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/section[1]/div[2]/section/div/button'))
        )
    except TimeoutException:
        pass

    while(True):
        if(len(driver.find_elements(By.XPATH, '//button[text()="Notify Me"]')) != 0):
            out =  "OUT OF STOCK"
            print("out of stock")
            break

        elif(len(driver.find_elements(By.XPATH, '//button[text()="Add to cart"]')) != 0):
            out =  "IN STOCK"
            print("in stock")
            break

        elif("404" in driver.current_url):
            out =  "BUY PAGE ERROR"
            print("error")
            break

        elif("?buyDisabled=1" in driver.current_url):
            out =  "BUY PAGE ERROR"
            print("error")
            break

    driver.close()

    driver.switch_to.window(main_tab)

    return (url, out)

def stock_check():
    start_time = time.time()

    # Load the Excel file
    file_path = "XiaomiStock.xlsx"  # Replace with the path to your local file
    sheet_name = "Products"

    # Load the specific sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    urls = [url for url in df['URL'] if pd.notna(url)]

    urls = urls[:12]

    with ProcessPoolExecutor(max_workers=4, initializer=init_worker) as executor:
        results = list(executor.map(checkURLParallel, urls))

    # Map results back to dataframe
    for url, status in results:
        df.loc[df['URL'] == url, 'Status'] = status

    date = datetime.now().strftime("(%Y-%m-%d)")

    base, ext = os.path.splitext(file_path)
    save_path = os.path.join("stock_checks", f"{base}{date}{ext}")

    # Save
    with pd.ExcelWriter(save_path, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Write timestamp to cell E2
        worksheet = writer.sheets[sheet_name]
        timestamp = datetime.now().strftime("Last checked: %Y-%m-%d %H:%M:%S")
        worksheet["E2"] = timestamp

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Status column updated successfully in {elapsed:.2f} seconds.")

    return (f"{base}{date}{ext}", save_path)

if __name__ == '__main__':
    start_time = time.time()

    # Load the Excel file
    file_path = "XiaomiStock.xlsx"  # Replace with the path to your local file
    sheet_name = "Products"

    # Load the specific sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    urls = [url for url in df['URL'] if pd.notna(url)]

    with ProcessPoolExecutor(max_workers=4, initializer=init_worker) as executor:
        results = list(executor.map(checkURLParallel, urls))

    # Map results back to dataframe
    for url, status in results:
        df.loc[df['URL'] == url, 'Status'] = status

    date = datetime.now().strftime("(%Y-%m-%d)")

    base, ext = os.path.splitext(file_path)
    ext = ".xls"
    save_path = os.path.join("stock_checks", f"{base}{date}{ext}")

    # Save
    with pd.ExcelWriter(save_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Write timestamp to cell E2
        worksheet = writer.sheets[sheet_name]
        timestamp = datetime.now().strftime("Last checked: %Y-%m-%d %H:%M:%S")
        worksheet["E2"] = timestamp

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Status column updated successfully in {elapsed:.2f} seconds.")
