
import re
import sys
import urllib
 
import requests
 
 
 
def getPage(keyword,page,n):
    page=page*n
    keyword=urllib.parse.quote(keyword, safe='/')
    url_begin= "http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word="
    url = url_begin+ keyword + "&pn=" +str(page) + "&gsm="+str(hex(page))+"&ct=&ic=0&lm=-1&width=0&height=0"
    return url
 
def get_onepage_urls(onepageurl):
    try:
        html = requests.get(onepageurl).text
    except Exception as e:
        print(e)
        pic_urls = []
        return pic_urls
    pic_urls = re.findall('"objURL":"(.*?)",', html, re.S)
    return pic_urls
 
 
def down_pic(pic_urls):
    """给出图片链接列表, 下载所有图片"""
    for i, pic_url in enumerate(pic_urls):
        try:
            pic = requests.get(pic_url, timeout=15)
            string =str(i + 1) + '.jpg'
            with open(string, 'wb') as f:
                f.write(pic.content)
                print('成功下载第%s张图片: %s' % (str(i + 1), str(pic_url)))
        except Exception as e:
            print('下载第%s张图片时失败: %s' % (str(i + 1), str(pic_url)))
            print(e)
            continue
 
 
if __name__ == '__main__':
    
    keyword = input("input key word:")
    page_begin=0
    page_number=30
    image_number=3
    all_pic_urls = []
    while 1:
        if page_begin>image_number:
            break
        print("第%d次请求数据",[page_begin])
        url=getPage(keyword,page_begin,page_number)
        onepage_urls= get_onepage_urls(url)
        page_begin += 1
 
        all_pic_urls.extend(onepage_urls)
 
    down_pic(list(set(all_pic_urls)))
