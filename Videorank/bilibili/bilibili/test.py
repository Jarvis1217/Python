import requests
from lxml import etree

url="https://www.bilibili.com/ranking?spm_id_from=333.851.b_7072696d61727950616765546162.3"

res=requests.get(url)
html=etree.HTML(res.content.decode())

aims=html.xpath('//ul[@class="rank-list"]/li')

for aim in aims:
    # rank/title/url/grade
    print(aim.xpath('div[@class="num"]/text()')[0])
    print(aim.xpath('div[@class="content"]/div[@class="info"]/a/text()')[0])
    print(aim.xpath('div[@class="content"]/div[@class="info"]/a/@href')[0])
    print(aim.xpath('div[@class="content"]/div[@class="info"]/div[@class="pts"]/div/text()')[0])