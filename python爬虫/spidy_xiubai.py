import requests
from bs4 import BeautifulSoup
 
# 获取html文档
def get_html(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    return response.text
    
# 获取笑话
def get_certain_joke(html,a):
    soup = BeautifulSoup(html, 'lxml')
    joke_content = soup.select('div.content')[a].get_text()
    return joke_content
 
url_joke = "https://www.qiushibaike.com"
html = get_html(url_joke)

for a in range(0,25):
    joke_content = get_certain_joke(html,a)
    print (joke_content)
