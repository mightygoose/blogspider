# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from blogspider.items import BlogspiderItem

import json
import os
import re

import pdb

DELETION_REGEX = "download|скачать|mp3"

LINKS_SELECTORS = '.navigation a:last-child::attr("href")'
POST_LINK_SELECTORS = '#dle-content table:nth-of-type(odd) .ntitle a::attr("href")'

POST_SELECTOR = '#dle-content ~ table:nth-of-type(1)'

POST_DATE_SELECTOR = ''
POST_TITLE_SELECTOR = '.ntitle::text'
POST_IMAGES_SELECTOR = '.news img::attr("src")'
POST_TAGS_SELECTOR = ''
POST_COMMENTS_SELECTOR = '#dlemasscomments'
POST_CONTENT_SELECTOR = '.news'
POST_EMBED_SELECTOR = 'object, iframe'



class XoroshoSpider(CrawlSpider):
    name = 'xorosho'
    allowed_domains = ['xorosho.com']
    start_urls = tuple(['http://www.xorosho.com/category/xoroshaya_muzika/'])
    visited = []
    counter = 0

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        return cls(
            settings=crawler.settings,
            *args, **kwargs
        )

    def __init__(self, settings=None, blogspot_urls_endpoint=None, *args, **kwargs):

        self.LINKS_SELECTORS = settings.get('LINKS_SELECTORS', LINKS_SELECTORS)
        self.POST_LINK_SELECTORS = settings.get('POST_LINK_SELECTORS', POST_LINK_SELECTORS)

        self.POST_SELECTOR = settings.get('POST_SELECTOR', POST_SELECTOR)

        self.POST_DATE_SELECTOR = settings.get('POST_DATE_SELECTOR', POST_DATE_SELECTOR)
        self.POST_TITLE_SELECTOR = settings.get('POST_TITLE_SELECTOR', POST_TITLE_SELECTOR)
        self.POST_IMAGES_SELECTOR = settings.get('POST_IMAGES_SELECTOR', POST_IMAGES_SELECTOR)
        self.POST_TAGS_SELECTOR = settings.get('POST_TAGS_SELECTOR', POST_TAGS_SELECTOR)
        self.POST_COMMENTS_SELECTOR = settings.get('POST_COMMENTS_SELECTOR', POST_COMMENTS_SELECTOR)
        self.POST_CONTENT_SELECTOR = settings.get('POST_CONTENT_SELECTOR', POST_CONTENT_SELECTOR)
        self.POST_EMBED_SELECTOR = settings.get('POST_EMBED_SELECTOR', POST_EMBED_SELECTOR)

        super(XoroshoSpider, self).__init__(*args, **kwargs)


    def parse(self, response):
        posts = response.css(self.POST_LINK_SELECTORS).extract()
        for post_link in posts:
            yield scrapy.Request(post_link, self.parse_post)

        links = response.css(self.LINKS_SELECTORS).extract();
        for link in links:
            yield scrapy.Request((link), self.parse)

    def parse_post(self, response):

        item = BlogspiderItem()

        item["crawler_name"] = "xorosho"

        item["scrapinghub_id"] = "{0}/{1}".format(os.getenv('SHUB_JOBKEY', ''), self.counter)
        self.counter = self.counter + 1

        post = response.css(self.POST_SELECTOR)

        item["url"] = response.url
        item["referer"] = response.request.headers['Referer']
        item["blog_host"] = response.request.headers['Referer'] #??
        item["date"] = '-'
        title = post.css(self.POST_TITLE_SELECTOR).extract()[0].encode("utf-8").strip()
        title_parts = re.sub(DELETION_REGEX, '', title).split("/")
        if(len(title_parts) is 1):
            title = title
            tags =[]
        else:
            title = title_parts[0].strip()
            tags = map(lambda x: x.strip(), title_parts[1].split(' - ')[0].split(','))
        item["title"] = title
        item["images"] = map(
            lambda x: "{0}{1}".format("http://xorosho.com", x.encode("utf-8")),
            post.css(self.POST_IMAGES_SELECTOR).extract()
        )
        item['tags'] = tags
        item["comments"] = response.css(self.POST_COMMENTS_SELECTOR).extract()
        item["content"] = post.css(self.POST_CONTENT_SELECTOR).extract()[0]
        item['embed'] = post.css(self.POST_EMBED_SELECTOR).extract()
        item["links"] = []

        #postprocessing
        item["badges"] = []
        if(item["title"] is ""):
            item["badges"].append("no-title")
        if(len(item['images']) is 0):
            item['badges'].append('no-image')
        if(len(item['embed']) > 0):
            item['badges'].append('has-embed')
        if(re.search("(?i)disc 2", item["content"])):
            item['badges'].append('multiple-discs')

        if(re.search("(?i)tracklist", item["content"]) \
                or re.search("(?i)disc 2", item["content"]) \
                or re.search("(?i)tracks :", item["content"]) \
                or re.search("(?i)track (?i)listing", item["content"])):
            item['badges'].append('has-tracklist')


        yield item

