from flask import Flask
import json
import requests
app = Flask(__name__)


def get_url():
    url = "https://bing.ioliu.cn/v1/rand?type=json"
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"
    }

    r = requests.get(url,headers = headers)

    content = json.loads(r.text).get("data").get("url")
    return content

@app.route('/')
def get_img():
    return get_url()


def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == "__main__":
    app.after_request(after_request)
    app.run()
