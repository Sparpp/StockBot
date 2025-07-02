from selenium import webdriver
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from urllib3.exceptions import ReadTimeoutError
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
    urlbuy = url + "buy"
    print(urlbuy)
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    try:
        driver.get(urlbuy)
    except (TimeoutError, ReadTimeoutError):
        return (url, "UNKNOWN ERROR")

    try:
        WebDriverWait(driver, 2, ignored_exceptions=[TimeoutException, TimeoutError]).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/section[1]/div[2]/section/div/button'))
        )
    except (TimeoutException, TimeoutError):
        return (url, "UNKNOWN ERROR")

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

    file_path = "XiaomiStock.xlsx"
    sheet_name = "Products"

    df = pd.read_excel(file_path, sheet_name=sheet_name)

    urls = [url for url in df['URL'] if pd.notna(url)]

    # Use python multiprocessing library to instantiate multiple worker instances to check webpages
    with ThreadPoolExecutor(max_workers=4, initializer=init_worker) as executor:
        results = list(executor.map(checkURLParallel, urls))

    for url, status in results:
        df.loc[df['URL'] == url, 'Status'] = status

    date = datetime.now().strftime("(%Y-%m-%d)")

    base, ext = os.path.splitext(file_path)
    save_path = os.path.join("stock_checks", f"{base}{date}{ext}")

    with pd.ExcelWriter(save_path, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        worksheet = writer.sheets[sheet_name]
        timestamp = datetime.now().strftime("Last checked: %Y-%m-%d %H:%M:%S")
        worksheet["E2"] = timestamp

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Status column updated successfully in {elapsed:.2f} seconds.")

    return (f"{base}{date}{ext}", save_path)

def stock_compare():
    became_out_of_stock = []
    became_in_stock = []
    became_error = []

    today = datetime.now()
    if today.weekday() != 0:
        prevday = today - timedelta(days=1)
    elif today.weekday() == 0:
        prevday = today - timedelta(days=3)

    last_date = prevday.strftime("(%Y-%m-%d)")
    now_date = datetime.now().strftime("(%Y-%m-%d)")

    base, ext = os.path.splitext("XiaomiStock.xlsx")
    last_path = os.path.join("stock_checks", f"{base}{last_date}{ext}")
    now_path = os.path.join("stock_checks", f"{base}{now_date}{ext}")

    df_last = pd.read_excel(last_path, sheet_name="Products")
    df_now = pd.read_excel(now_path, sheet_name="Products")

    for index in range(len(df_last)):
        last_status = df_last.at[index, 'Status']
        now_status = df_now.at[index, 'Status']
        title = df_now.at[index, 'Title']

        if last_status != now_status:
            if now_status == "OUT OF STOCK":
                became_out_of_stock.append(title)
            elif now_status == "IN STOCK":
                became_in_stock.append(title)
            elif now_status == "BUY PAGE ERROR":
                became_error.append(title)

    output = []

    if not became_out_of_stock and not became_in_stock and not became_error:
        return "There have been no changes in stock since last check."

    if became_out_of_stock:
        output.append(
            "The products that have gone out of stock are: " + ", ".join(became_out_of_stock) + ".\n"
        )
    if became_in_stock:
        output.append(
            "\nThe products that have come back in stock are: " + ", ".join(became_in_stock) + ".\n"
        )
    if became_error:
        output.append(
            "\nThe products that are now returning an error are: " + ", ".join(became_error) + "."
        )

    return " ".join(output)