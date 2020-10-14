import requests
from lxml import etree
import re
import os

def clean(lt):
    res = []
    for i in lt:
        res.append(int(re.findall(r"\d+\.?\d*", i)[0]))

    return res


url = input("歌单url:").replace("/#","")

html = requests.get(url).content
txt = etree.HTML(html)

for i in txt:
    song_id = clean(i.xpath("//ul[@class='f-hide'][1]/li/a/@href"))
    song_name = i.xpath("//ul[@class='f-hide'][1]/li/a/text()")

# # 输出歌单信息
# for i in range(len(song_id)):
#     print("name:{}-id:{}".format(song_name[i], song_id[i]))

# 保存MP3
path="./mp3"
if not os.path.exists(path):
    os.mkdir(path)

for i in range(len(song_id)):
    try:
        save_url="http://music.163.com/song/media/outer/url?id="+str(song_id[i])+".mp3"
        file_name=song_name[i]+".mp3"
        res=requests.get(save_url)

        with open("./mp3/"+file_name,'ab') as fl:
            fl.write(res.content)
            print("{}下载成功".format(song_name[i]))
            fl.flush()

    except Exception as e:
       print("{}下载失败".format(song_name[i]))