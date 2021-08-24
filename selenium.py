from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if __name__ == '__main__':
    # 无界面启动
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    br = webdriver.Chrome(chrome_options=chrome_options)
    br.get("http://localhost:8666/leaf_xyzl/leaf.lview")

    # 模拟登录
    br.find_element_by_xpath('//*[@id="loginForm"]/div[2]/div[1]/input').send_keys('admin')
    br.find_element_by_xpath('//*[@id="password"]').send_keys('1')
    br.find_element_by_xpath('//*[@id="loginForm"]/div[2]/div[4]/button').click()

    print(br.page_source)
