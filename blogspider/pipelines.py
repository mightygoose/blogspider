# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import urllib, urllib2
import json


import pdb


class MightyGoosePipeline(object):

    def __init__(self, settings):
        self.settings = settings
        self.MG_PIPELINE_URL = self.settings.get('MG_PIPELINE_URL')

        print 'pipelining items to {0}'.format(self.MG_PIPELINE_URL)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings=crawler.settings,
        )


    def process_item(self, item, spider):
        values = {
            "title": item['title'].encode("utf-8").strip(),
            "badges": json.dumps(item['badges']),
            "url": item['url'],
            "tags": json.dumps(item['tags']),
            "sh_key": item['scrapinghub_id'],
            "crawler_name": item['crawler_name'],
            "embed": json.dumps(item['embed']),
            "images": json.dumps(item['images']),
            "content": json.dumps(item['content']),
            "comments": json.dumps(item['comments'])
        }
        headers = {}

        data = urllib.urlencode(values)
        req = urllib2.Request(self.MG_PIPELINE_URL, data, headers)
        response = urllib2.urlopen(req, timeout = 5)
        response_body = response.read()
        try:
            [status, badges] = json.loads(response_body)
            item["status"] = status
            item["badges"] = badges
        except:
            item["status"] = "mightygoose_bad_response"

        return item


