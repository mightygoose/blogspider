# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from blogspider.items import BlogspiderItem

import urllib, urllib2
import json
import os
import re


import pdb

POSTS_BLOCK_SELECTORS = '.date-outer .post-outer'
POST_LINK_SELECTORS = '.post-title a::attr("href")'

POST_DATE_SELECTOR = '.date-header ::text'
POST_TITLE_SELECTOR = '.post-title ::text'
POST_IMAGES_SELECTOR = 'img::attr("src")'
POST_TAGS_SELECTOR = '.post-labels a::text'
POST_COMMENTS_SELECTOR = '.comments .comment-thread li'
POST_CONTENT_SELECTOR = '.post'
POST_EMBED_SELECTOR = 'object, iframe'

LINKS_SELECTORS = ' \
    .widget.BlogList .blog-title > a::attr("href"), \
    .widget.LinkList a::attr("href") \
'
PREV_POSTS_LINKS_SELECTORS = '.blog-pager-older-link::attr("href")'


DELETION_MAP = [
        "^[-|#|=|+|.]{1,}", "[-|#|=|+]{1,}$",
        "^\*+", "\*+$",
        "(?i)genre: ", "(?i)label: ", "(?i)country: ",
        "[^\w -]",
        "[", "]"

]

class BlogspotSpider(CrawlSpider):
    name = 'blogspot'
    visited = []
    counter = 0
    start_urls = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        return cls(
            settings=crawler.settings,
            *args, **kwargs
        )

    def __init__(self, settings=None, blogspot_urls_endpoint=None, *args, **kwargs):

        self.POSTS_BLOCK_SELECTORS = settings.get('POSTS_BLOCK_SELECTORS', POSTS_BLOCK_SELECTORS)
        self.POST_LINK_SELECTORS = settings.get('POST_LINK_SELECTORS', POST_LINK_SELECTORS)
        self.LINKS_SELECTORS = settings.get('LINKS_SELECTORS', LINKS_SELECTORS)

        self.POST_DATE_SELECTOR = settings.get('POST_DATE_SELECTOR', POST_DATE_SELECTOR)
        self.POST_TITLE_SELECTOR = settings.get('POST_TITLE_SELECTOR', POST_TITLE_SELECTOR)
        self.POST_IMAGES_SELECTOR = settings.get('POST_IMAGES_SELECTOR', POST_IMAGES_SELECTOR)
        self.POST_TAGS_SELECTOR = settings.get('POST_TAGS_SELECTOR', POST_TAGS_SELECTOR)
        self.POST_COMMENTS_SELECTOR = settings.get('POST_COMMENTS_SELECTOR', POST_COMMENTS_SELECTOR)
        self.POST_CONTENT_SELECTOR = settings.get('POST_CONTENT_SELECTOR', POST_CONTENT_SELECTOR)
        self.POST_EMBED_SELECTOR = settings.get('POST_EMBED_SELECTOR', POST_EMBED_SELECTOR)

        self.blogspot_urls_endpoint = settings.get('BLOGSPOT_URLS_ENDPOINT', blogspot_urls_endpoint)

        print 'requsting urls from {0}'.format(self.blogspot_urls_endpoint)

        req = urllib2.Request(self.blogspot_urls_endpoint)
        response = urllib2.urlopen(req)
        response_body = response.read()
        urls = json.loads(response_body)
        self.start_urls = tuple(urls)

        print 'starting with urls: {0}'.format(json.dumps(urls))

        super(BlogspotSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        posts = response.css(POSTS_BLOCK_SELECTORS)
        for post in posts:
            post_link = post.css(POST_LINK_SELECTORS).extract()[0]
            if(not post_link in self.visited):
                yield scrapy.Request(post_link, self.parse_post)


        links = response.css(self.LINKS_SELECTORS).extract()
        try:
            links.append(
                    response.css(PREV_POSTS_LINKS_SELECTORS).extract()[0]
            )
        except:
            pass
        for link in links:
            if re.match(r'(.+).blogspot.(.+)\/', link) is None:
                continue
            if(not link in self.visited):
                yield scrapy.Request(link, self.parse)


    def parse_post(self, response):
        item = BlogspiderItem()
        post = response.css('.date-outer')

        item["crawler_name"] = "BlogPostItem"

        item["scrapinghub_id"] = "{0}/{1}".format(os.getenv('SHUB_JOBKEY', ''), self.counter)
        self.counter = self.counter + 1

        item["url"] = response.url
        item["referer"] = response.request.headers['Referer']
        item["blog_host"] = response.request.headers['Referer']
        item["date"] = post.css(self.POST_DATE_SELECTOR).extract()[0]
        item["title"] = post.css(self.POST_TITLE_SELECTOR).extract()[0]
        item["images"] = post.css(self.POST_IMAGES_SELECTOR).extract()
        item["raw_tags"] = response.css(self.POST_TAGS_SELECTOR).extract()

        #FIXME: should be done on mg side
        item['tags'] = [re.sub('|'.join(DELETION_MAP), '', tag) for tag in item['raw_tags']]

        item["comments"] = post.css(self.POST_COMMENTS_SELECTOR).extract()
        item["content"] = post.css(self.POST_CONTENT_SELECTOR).extract()[0]
        item['embed'] = post.css(self.POST_EMBED_SELECTOR).extract()

        #postprocessing
        #FIXME: below should be processed on mg side
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

