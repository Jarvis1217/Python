import urllib
from bs4 import BeautifulSoup
import requests

url = "https://s.weibo.com/top/summary/summary?cate=realtimehot"

html = requests.get(url)
bs = BeautifulSoup(html.content, "lxml")

content = bs.find("div", id="pl_top_realtimehot").find_all("a")

news = []
for con in content:
    news.append(con.get_text())

for i in news:
    print(i.replace("#", ""))
    print("https://s.weibo.com/weibo?q=%23"+urllib.parse.quote(i.replace("#", ""))+"%23")