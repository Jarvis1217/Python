import time
import openpyxl
from lxml import etree
from selenium import webdriver

baseUrl = 'https://www.anjuke.com/fangjia/'
cities = ['beijing', 'shanghai', 'tianjin', 'chongqing']

# 创建工作表保存数据
wb = openpyxl.Workbook()

# Selenium加载chrome驱动
br = webdriver.Chrome()

for city in cities:
    ws = wb.create_sheet()
    ws.title = city
    for year in range(2011, 2021):
        url = baseUrl+city+str(year)
        br.get(url)
        print("访问链接:" + url)
        time.sleep(3)

        # 获取网页源码解析数据
        html = etree.HTML(br.page_source)
        aims = html.xpath('//div[@class="fjlist-box boxstyle2"]/ul/li')
        for aim in aims:
            date = aim.xpath('a/b/text()')[0]
            price = aim.xpath('a/span/text()')[0]
            ws.append([date, price])
            print(city + date + "保存成功")
            time.sleep(3)

br.close()
del wb["Sheet"]
wb.save("Data.xlsx")
