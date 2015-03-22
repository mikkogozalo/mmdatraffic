# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import create_engine

from scrapy.exceptions import DropItem
from scrapy import log


class GuidPipeline(object):

    def open_spider(self, spider):
        self.guid_monitor = {}

    def process_item(self, item, spider):
        if all(
                field in item for field in
                    ['name', 'direction', 'line', 'guid']
            ):
            slug = "/".join(
                [item['name'],
                item['direction'],
                item['line']]
            )
            if slug not in self.guid_monitor:
                self.guid_monitor[slug] = []
            if item['guid'] in self.guid_monitor[slug]:
                raise DropItem('Crawled already')
            self.guid_monitor[slug].append(item['guid'])
        else:
            log.msg('Item is not complete %s' % item)
        return item
