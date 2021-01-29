from flask import Flask
import requests
from lxml import etree

app = Flask(__name__)


# 设置允许跨域
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# 设置访问路由
@app.route('/')
def get_content():
    url = "https://s.weibo.com/top/summary?Refer=top_hot&topnav=1&wvr=6"
    resp = requests.get(url)

    # 把返回的数据转换为可以被xpath解析的对象
    html = etree.HTML(resp.text)

    # 解析所有热搜内容
    content = html.xpath('//*[@id="pl_top_realtimehot"]/table/tbody//tr/td[2]/a/text()')

    return {"content": content}


if __name__ == "__main__":
    app.after_request(after_request)
    app.config["JSON_AS_ASCII"] = False
    app.run()
