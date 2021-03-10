# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WymusicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    playlist_name=scrapy.Field()
    playlist_id=scrapy.Field()
    music_name=scrapy.Field()
    music_id=scrapy.Field()

    pass
