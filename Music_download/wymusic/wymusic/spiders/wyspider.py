import scrapy
from urllib3 import request

from wymusic.items import WymusicItem
import re

class WyspiderSpider(scrapy.Spider):
    name = 'wyspider'
    allowed_domains = ['music.163.com']
    start_urls = ['https://music.163.com/discover/playlist']
    page=1

    def parse(self, response):

        # 清洗song_id
        def clean(lt):
            res = []
            for i in lt:
                res.append(int(re.findall(r"\d+\.?\d*", i)[0]))
            return res

        current_page=response.xpath("//ul[@class='m-cvrlst f-cb']/li")

        for aim in current_page:
            msc=WymusicItem()

            msc['playlist_name']=aim.xpath("div[@class='u-cover u-cover-1']/a/@title").extract()[0]
            msc['playlist_id']=clean(aim.xpath("div[@class='u-cover u-cover-1']/a/@href").extract())[0]

            link=aim.xpath("div[@class='u-cover u-cover-1']/a/@href").extract()[0]
            url="https://music.163.com"+link
            if url:
                yield scrapy.Request(url,meta={'item':msc},callback=self.parse_music)

            pass

        next_page=response.xpath("//div[@class='u-page']/a[@class='zbtn znxt']/@href").extract()
        if next_page:
            self.page+=1
            next_link=response.urljoin(next_page[0])
            yield scrapy.Request(next_link,callback=self.parse)

    def parse_music(self, response):

        # 清洗song_id
        def clean(lt):
            res = []
            for i in lt:
                res.append(int(re.findall(r"\d+\.?\d*", i)[0]))
            return res

        msc=response.meta['item']
        aims=response.xpath("//ul[@class='f-hide'][1]/li/a")

        for aim in aims:
            msc['music_name']=aim.xpath("text()").extract()
            msc['music_id']=clean(aim.xpath("@href").extract())[0]

            yield msc

        pass