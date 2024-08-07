import re
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def extract_room_and_area(room_text):
    match = re.search(r'(\d+室)\s+(\d+\.?\d*㎡)', room_text)
    if match:
        return match.group(1), match.group(2)
    return None, None

driver = webdriver.Chrome()


all_data = {
    'Title': [],
    'Room': [],
    'Area': [],
    'Rent': [],
    'Address': [],
    'Subway_Distance': []
}


driver.get('URL')
wait = WebDriverWait(driver, 10)

num_pages = 5

for _ in range(num_pages):

    time.sleep(random.uniform(3, 6))

    Titles = driver.find_elements(By.XPATH, '//div[@class="des"]/h2[1]/a[1]')
    Room = driver.find_elements(By.XPATH, '//div[@class="des"]/p[1]')
    Rent = driver.find_elements(By.XPATH, '//div[@class="money"]/b[1]')
    Address = driver.find_elements(By.XPATH, '//div[@class="des"]/p[2]/a[1]')
    Subway = driver.find_elements(By.XPATH, '//div[@class="des"]/p[2]')

    for title, room, rent, address, subway in zip(Titles, Room, Rent, Address, Subway):
        room_type, room_area = extract_room_and_area(room.text)
        all_data['Title'].append(title.text)
        all_data['Room'].append(room_type)
        all_data['Area'].append(room_area)
        all_data['Rent'].append(rent.text)
        all_data['Address'].append(address.text)
        all_data['Subway_Distance'].append(subway.text)


    while True:
        try:
            next_page = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="next"]/span[text()="下一页"]')))
            break
        except:
            driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(random.uniform(1, 2))

    next_page.click()


    time.sleep(random.uniform(3, 6))

driver.quit()


df = pd.DataFrame(all_data)
df.to_csv('YOUR SAVING PATH', index=False)
