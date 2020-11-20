import time
import requests
import pandas as pd
from lxml import etree

baseUrl = 'https://maoyan.com/board/4?offset='
headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
}

name = ['电影名称', '主演', '上映时间', '评分']
result = []

for i in range(0, 100, 10):
    url = baseUrl + str(i)

    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding

    html = etree.HTML(r.text)
    aims = html.xpath("//dl[@class='board-wrapper']/dd")

    for aim in aims:
        movieName = aim.xpath("div[@class='board-item-main']/div/div[1]/p[1]/a/text()")[0]
        actor = aim.xpath("div[@class='board-item-main']/div/div[1]/p[2]/text()")[0].replace(" ", "").replace('\n', '').replace('主演：', '')
        movieTime = aim.xpath("div[@class='board-item-main']/div/div[1]/p[3]/text()")[0].replace("上映时间：", "")
        g1 = aim.xpath("div[@class='board-item-main']/div/div[2]/p/i[1]/text()")[0]
        g2 = aim.xpath("div[@class='board-item-main']/div/div[2]/p/i[2]/text()")[0]
        movieGrade = g1 + g2
        lst = [movieName, actor, movieTime, movieGrade]
        result.append(lst)
        print(lst)
        time.sleep(3)

test = pd.DataFrame(columns=name, data=result)
test.to_csv("../Data.csv")
