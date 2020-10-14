import requests
from bs4 import BeautifulSoup

url = "https://movie.douban.com/chart"
headers = {"User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 QIHU 360SE"
           }

html = requests.get(url, headers=headers)
bs = BeautifulSoup(html.content, 'lxml')

content1 = bs.find("ul", id='listCont2').find_all('a')
content2 = bs.find("ul", id='listCont1').find_all('a')

# 一周口碑榜
week = []
for con in content1:
    week.append(con.get_text().replace('\n', '').replace(" ", ""))

# 北美票房榜
north = []
for con in content2:
    north.append(con.get_text().replace('\n', '').replace(" ", ""))

print("一周口碑榜:", week)
print("北美票房榜:", north)
