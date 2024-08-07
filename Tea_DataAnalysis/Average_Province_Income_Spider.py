import requests
import pandas as pd
from lxml import etree

header = {
    'user-agent': 'YOUR PARAMETER ',
}
url = 'URL'


response = requests.get(url, headers=header)
response.encoding = 'utf-8' 

html = etree.HTML(response.text)

table_xpath = '//table[contains(@class, "display")]'
tables = html.xpath(table_xpath)

table_data = []
headers = []

def extract_table_data(table):

    header_xpath = './/thead//tr//th'
    headers = [th.text.strip() for th in table.xpath(header_xpath)]
    
    row_xpath = './/tbody//tr'
    rows = table.xpath(row_xpath)
    data = []
    
    for row in rows:
        cell_xpath = './/td//a'
        cells = row.xpath(cell_xpath)
        if len(cells) > 0:
            row_data = [cell.text.strip() for cell in cells]
            data.append(row_data)
    
    return headers, data

if tables:

    table = tables[0]
    headers, table_data = extract_table_data(table)
else:
    print("未找到符合条件的表格")
    headers = []
    table_data = []

if headers and table_data:
    df = pd.DataFrame(table_data, columns=headers)
    df.to_csv("YOUR SAVING PATH", index=False)
    print("数据已成功保存到CSV文件中")
else:
    print("未能提取表格数据")
