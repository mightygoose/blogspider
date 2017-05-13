# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from blogspider.items import BlogspiderItem

import json
import os
import re

import pdb

DELETION_MAP = [
        "^[-|#|=|+|.]{1,}", "[-|#|=|+]{1,}$",
        "^\*+", "\*+$",
        "(?i)genre: ", "(?i)label: ", "(?i)country: ",
        "[^\w -]",
        "[", "]"

]

LINKS_SELECTORS = '#content .rounded-block + .box .pagination > span.next a::attr("href")'
POST_LINK_SELECTORS = '.article .more.clearfix div:first-child a::attr("href")'

POST_SELECTOR = '.article'

POST_DATE_SELECTOR = '.news_date::attr("title")'
POST_TITLE_SELECTOR = '[itemprop="headline"]::text'
POST_IMAGES_SELECTOR = '.article-image img::attr("src")'
POST_TAGS_SELECTOR = '.tags a::text'
POST_COMMENTS_SELECTOR = '.comments_list'
POST_CONTENT_SELECTOR = 'div[itemprop="articleBody"]'
POST_EMBED_SELECTOR = 'object, iframe'


class NnmSpider(CrawlSpider):
    name = 'nnm'
    allowed_domains = ['nnm.me']
    start_urls = tuple(['http://muzic.nnm.me/'])
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

        super(NnmSpider, self).__init__(*args, **kwargs)


    def parse(self, response):
        posts = response.css(self.POST_LINK_SELECTORS).extract()
        for post_link in posts:
            yield scrapy.Request(post_link, self.parse_post)

        links = response.css(self.LINKS_SELECTORS).extract();
        for link in links:
            yield scrapy.Request('{0}{1}'.format('http://muzic.nnm.me', link), self.parse)

    def parse_post(self, response):

        item = BlogspiderItem()

        item["crawler_name"] = "nnm"

        item["scrapinghub_id"] = "{0}/{1}".format(os.getenv('SHUB_JOBKEY', ''), self.counter)
        self.counter = self.counter + 1

        post = response.css(self.POST_SELECTOR)

        item["url"] = response.url
        item["referer"] = response.request.headers['Referer']
        item["blog_host"] = response.request.headers['Referer']
        item["date"] = post.css(self.POST_DATE_SELECTOR).extract()[0].encode("utf-8").strip()
        item["title"] = post.css(self.POST_TITLE_SELECTOR).extract()[0].encode("utf-8").strip()
        item["images"] = post.css(self.POST_IMAGES_SELECTOR).extract()
        item["raw_tags"] = response.css(self.POST_TAGS_SELECTOR).extract()
        item['tags'] = [re.sub('|'.join(DELETION_MAP), '', tag) for tag in item['raw_tags']]
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
