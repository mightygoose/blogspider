# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from blogspider.items import BlogspiderItem

import pdb


class NnmSpider(CrawlSpider):
    name = 'nnm'
    allowed_domains = ['ya.ru']
    start_urls = ['http://www.ya.ru/']


    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        return cls(
            settings=crawler.settings,
            *args, **kwargs
        )

    def __init__(self, settings=None, blogspot_urls_endpoint=None, *args, **kwargs):

        self.blogspot_urls_endpoint = settings.get('BLOGSPOT_URLS_ENDPOINT', blogspot_urls_endpoint)

        super(NnmSpider, self).__init__(*args, **kwargs)
        print '\n\n'
        print 'urls enpoint'
        print self.blogspot_urls_endpoint
        print '\n\n'

    def parse(self, response):
        i = BlogspiderItem()
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
