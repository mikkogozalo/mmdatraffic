# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import create_engine

from scrapy.exceptions import DropItem
from scrapy import log


class LatestPipeline(object):

    def open_spider(self, spider):
        self.guid_monitor = {}

    def process_item(self, item, spider):
        if all(
                field in item for field in
                    ['name', 'direction', 'line', 'timestamp']
            ):
            slug = "/".join(
                [item['name'],
                item['direction'],
                item['line']]
            )
            if self.guid_monitor.get(slug, 0) >= item['timestamp']:
                raise DropItem('We already have this time')
            else:
                self.guid_monitor[slug] = item['timestamp']
            return item