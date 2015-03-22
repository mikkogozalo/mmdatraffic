# -*- coding: utf-8 -*-
import time

from scrapy import Spider, signals
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy.exceptions import DontCloseSpider

from mmdatraffic.utils import get_first
from mmdatraffic.items import IntensityItemLoader

class MmdaTrafficSpider(Spider):
    name = 'mmdatraffic'
    allowed_domains = ['mmdatraffic.interaksyon.com/']
    start_urls = ['http://mmdatraffic.interaksyon.com/system-view.php']

    last_scrape = None

    def parse(self, response):
        pass

class MmdaTrafficRSSSpider(Spider):
    name = 'mmdatraffic_rss'
    allowed_domains = ['mmdatraffic.interaksyon.com']
    start_urls = ['http://mmdatraffic.interaksyon.com/livefeed/']

    def __init__(self, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.scrape_again, signals.spider_idle)

    def parse(self, response):
        self.last_scrape = time.time()
        sel = Selector(text=response.body.replace('pubDate', 'timestamp'))
        points = sel.xpath('//item')
        for point in points:
            title = get_first(point, './title/text()')
            title_comps = title.split('-')
            line = title_comps[0]
            name = "-".join(title_comps[1:-1])
            direction = title_comps[-1]
            iil = IntensityItemLoader(selector=point)
            iil.add_value('name', name)
            iil.add_value('line', line)
            iil.add_value('direction', direction)
            iil.add_xpath('intensity', './description/text()')
            iil.add_xpath('guid', './guid/text()')
            iil.add_xpath('timestamp', './timestamp/text()')
            yield iil.load_item()

    def scrape_again(self, spider):
        if time.time() - self.last_scrape >= 20:
            self.crawler.engine.schedule(
                Request(self.start_urls[0], dont_filter=True),
                spider
            )
        raise DontCloseSpider
