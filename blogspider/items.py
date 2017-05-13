# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BlogspiderItem(scrapy.Item):
    crawler_name = scrapy.Field()
    scrapinghub_id = scrapy.Field()
    status = scrapy.Field()
    badges = scrapy.Field()
    embed = scrapy.Field()
    url = scrapy.Field()
    referer = scrapy.Field()
    blog_host = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    images = scrapy.Field()
    tags = scrapy.Field()
    raw_tags = scrapy.Field()
    content = scrapy.Field()
    comments = scrapy.Field()
    links = scrapy.Field()
