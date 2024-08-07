import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import random

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
       Object.defineProperty(navigator, 'webdriver', {
         get: () => false
       })
     """
})

url = "URL"
driver.get(url)

time.sleep(22)

all_data = {
    'Product_Name': [],
    'Product_Price': [],
    'Product_Sales': [],
    'Product_Origin': [],
}

num_page = 5

for _ in range(num_page):
    time.sleep(random.uniform(3, 6))
    
    Product_Name = driver.find_elements(By.XPATH, '//div[@class="Title--title--jCOPvpf "]/span[1]')
    Product_Price = driver.find_elements(By.XPATH, '//div[@class="Price--priceWrapper--Q0Dn7pN "]/div[1]/span[1]')
    Product_Sales = driver.find_elements(By.XPATH, '//div[@class="Price--priceWrapper--Q0Dn7pN "]/span[2]')
    Product_Origin = driver.find_elements(By.XPATH, '//div[@class="Price--priceWrapper--Q0Dn7pN "]/div[2]/span[1]')

    for product_name, product_price, product_sales, product_origin in zip(Product_Name, Product_Price, Product_Sales, Product_Origin):
        all_data['Product_Name'].append(product_name.text)
        all_data['Product_Price'].append(product_price.text)
        all_data['Product_Sales'].append(product_sales.text)
        all_data['Product_Origin'].append(product_origin.text)

    Next_Button = driver.find_element(By.XPATH, '//button[contains(@class, "next-next")]')
    Next_Button.click()

    time.sleep(random.uniform(3, 6))

driver.quit()

df = pd.DataFrame(all_data)
df.to_csv(r"YOUR SAVING PATH", index=False)
