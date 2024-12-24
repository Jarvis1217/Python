import time
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ChromeOptions

url = "https://news.cctv.com/"

# 无可视化界面
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

# 规避检测
option = ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])

bro = webdriver.Chrome()
bro.get('https://jingji.cctv.com/')
x = int(input('请输入需要爬取的页数:'))

i = 1
while i < x:
    bro.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div[2]/div[3]/div/div[3]/div/div[3]/i').click()
    time.sleep(5)
    i = i + 1

br = webdriver.Chrome()

br.get(url)

# 等待页面加载js代码
time.sleep(5)

# 模拟点击 "点击加载更多"
button = br.find_element_by_xpath("//div[@class='ELMTNPMkWvfnaiVjn2XT9PVP190719']/div/div[3]/p")
button.click()

# 获取渲染后的网页源码
page = br.page_source

# xpath解析
html = etree.HTML(page)
aims = html.xpath("//ul[@id='newslist']/li")

for aim in aims:
    print(aim.xpath("div[2]/h3/a/text()"))

br.close()
