import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

time.sleep(10)


login_button = driver.find_element(By.XPATH, '//*[@id="NormalLoginBtn"]/span[3]/a')
login_button.click()

accounts = driver.find_element(By.XPATH, '//*[@id="loginname"]')
accounts.send_keys('YOUR ACCOUNT')

time.sleep(5)
password = driver.find_element(By.XPATH, '//*[@id="password"]')
password.send_keys('YOUR PASSWORD')

agree = driver.find_element(By.XPATH, '//*[@id="isread_em"]')
agree.click()

time.sleep(2)

login_button = driver.find_element(By.XPATH, '//*[@id="login_btn_withPwd"]')
login_button.click()

time.sleep(20)

driver.get('URL AFTER LOGIN')

time.sleep(10)

all_data = {
    'Jobname': [],
    'Jobcompany': [],
    'Area': [],
    'Salary': [],
    'Jobcontent': [],
}

num_page = 5

for _ in range(num_page):
    time.sleep(random.uniform(3, 6))

    Jobname = driver.find_elements(By.XPATH, '//div[@class="e sensors_exposure "]/p[1]/span[1]/a[1]')
    Jobcompany = driver.find_elements(By.XPATH, '//div[@class="e sensors_exposure "]/p[1]/a[1]')
    Salary = driver.find_elements(By.XPATH, '//div[@class="e sensors_exposure "]/p[1]/span[3]')
    Area = driver.find_elements(By.XPATH, '//div[@class="e sensors_exposure "]/p[1]/span[2]')
    Jobcontent = driver.find_elements(By.XPATH, '//div[@class="e sensors_exposure "]/p[3]')

    for jobname, jobcompany, salary, area, jobcontent in zip(Jobname, Jobcompany, Salary, Area, Jobcontent):
        all_data['Jobname'].append(jobname.text)
        all_data['Jobcompany'].append(jobcompany.text)
        all_data['Salary'].append(salary.text)
        all_data['Area'].append(area.text)
        all_data['Jobcontent'].append(jobcontent.text)


    while True:
        try:
            next_page = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="p_in"]/ul/li[@class="bk"][2]/a'))
            )
            next_page.click()
            break
        except Exception as e:
            print(f"Error: {e}. Trying to scroll.")
            driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(random.uniform(1, 2))

    time.sleep(random.uniform(3, 6))

driver.quit()


df = pd.DataFrame(all_data)
df.to_csv(r"YOUR SAVING PATH", index=False)
