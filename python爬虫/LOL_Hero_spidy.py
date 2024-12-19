import requests
import json
import random

url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
html = requests.get(url)

js = json.loads(html.content)

heros = []
for i in range(len(js["hero"])):
    heros.append("{} - {}".format(js["hero"][i]["name"], js["hero"][i]["title"]))

for i,h in enumerate(heros):
    print(f"{i+1}.{h}")
