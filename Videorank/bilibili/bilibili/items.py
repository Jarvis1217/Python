# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BilibiliItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    rank=scrapy.Field()     # 视频排名
    title=scrapy.Field()    # 视频标题
    url=scrapy.Field()      # 视频链接
    grade=scrapy.Field()    # 视频综合评分

    pass
