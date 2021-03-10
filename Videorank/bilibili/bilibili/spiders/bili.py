import scrapy

from ..items import BilibiliItem


class BiliSpider(scrapy.Spider):
    name = 'bili'
    allowed_domains = ['bilibili.com']
    start_urls = ['https://www.bilibili.com/ranking?spm_id_from=333.851.b_7072696d61727950616765546162.3']

    def parse(self, response):

        current=response.xpath('//ul[@class="rank-list"]/li')

        for aim in current:
            vid=BilibiliItem()
            vid['rank']=aim.xpath('div[@class="num"]/text()').extract()[0]
            vid['title']=aim.xpath('div[@class="content"]/div[@class="info"]/a/text()').extract()[0]
            vid['url']=aim.xpath('div[@class="content"]/div[@class="info"]/a/@href').extract()[0]
            vid['grade']=aim.xpath('div[@class="content"]/div[@class="info"]/div[@class="pts"]/div/text()').extract()[0]

            yield vid

        pass
