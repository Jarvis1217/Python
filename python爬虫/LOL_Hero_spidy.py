import requests
import json
import random

url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
html = requests.get(url)

js = json.loads(html.content)

hero = []
for i in range(len(js["hero"])):
    hero.append("{}-{}".format(js["hero"][i]["name"], js["hero"][i]["title"]))

# for i in range(0,140,10):
#     print(hero[i:i+10])
# print(hero[-8:])

print("回车键刷新")
while True:
    print(random.sample(hero, 3))
    ch = input("")
    if ch == "\n":
        pass
