import os
import requests
from lxml import etree

# 下载页码
url = "https://wallhaven.cc/toplist?page=1"
headers = {
    'user-agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'
}

html = requests.get(url, headers=headers).content

txt = etree.HTML(html)
aims = txt.xpath('//section[@class="thumb-listing-page"]/ul/li')

path = './images'
if not os.path.exists(path):
    os.mkdir(path)

for aim in aims:
    name = aim.xpath('figure/@data-wallpaper-id')
    url = aim.xpath('figure/a/@href')

    html = requests.get(url[0], headers=headers).content

    txt = etree.HTML(html)
    save_url = txt.xpath('//section[@id="showcase"]/div[1]/img/@src')

    img = requests.get(save_url[0], headers=headers)
    with open(path + '/' + name[0] + '.jpg', 'wb') as f:
        f.write(img.content)
        print("下载成功:", name)