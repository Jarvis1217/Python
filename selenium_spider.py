from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

if __name__ == '__main__':
    url = "https://s.weibo.com/top/summary?cate=realtimehot"

    # 无界面启动
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    br = webdriver.Chrome(options=chrome_options)
    br.get(url)
    WebDriverWait(br, 10).until(EC.title_contains(u"热搜榜"))
    resp = br.page_source
    br.close()

    html = etree.HTML(resp)

    text_aims = html.xpath('//*[@id="pl_top_realtimehot"]/table/tbody//tr/td[2]/a/text()')
    url_aims = html.xpath('//*[@id="pl_top_realtimehot"]/table/tbody//tr/td[2]/a/@href')

    for idx, txt in enumerate(text_aims):
        print(str(idx) + "." + txt + ": " + "https://s.weibo.com/" + url_aims[idx] + "\n")
