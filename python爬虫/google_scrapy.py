import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlencode
import json

class GoogleSearchSpider(scrapy.Spider):
    name = "google_search"

    def __init__(self, query=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query = query
        self.base_url = "https://www.google.com/search"
        self.results = []

    def start_requests(self):
        params = {"q": self.query, "hl": "en"}
        url = f"{self.base_url}?{urlencode(params)}"
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        search_results = response.css("div.tF2Cxc")

        for result in search_results:
            title = result.css("h3::text").get()
            link = result.css("a::attr(href)").get()
            snippet_spans = result.css("div.VwiC3b span")
            snippet_texts = [span.xpath("string(.)").get() for i,span in enumerate(snippet_spans) if i != 1]
            snippet = ''.join(snippet_texts)

            if title and link:
                self.results.append({
                    "标题": title,
                    "链接": link,
                    "简介": snippet
                })

    def closed(self, reason):
        print(json.dumps(self.results, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    search_query = input("请输入搜索关键词: ")

    process = CrawlerProcess(settings={
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "LOG_LEVEL": "ERROR",
    })
    process.crawl(GoogleSearchSpider, query=search_query)
    process.start()
