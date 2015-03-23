# -*- coding: utf-8 -*-
import time
from urlparse import urljoin
import json

from scrapy import Spider, signals
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy.exceptions import DontCloseSpider

from mmdatraffic.utils import get_first
from mmdatraffic.items import IntensityItemLoader

class MmdaTrafficSpider(Spider):
    name = 'mmdatraffic'
    allowed_domains = ['mmdatraffic.interaksyon.com']
    start_urls = ['http://mmdatraffic.interaksyon.com/system-view.php']

    mapping = {}

    def __init__(self, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.scrape_traffic, signals.spider_idle)
        self.last_scrape = time.time() - 20

    def start_requests(self):
        yield Request(self.start_urls[0], self.initialize_lines)

    def initialize_lines(self, response):
        lines = response.xpath(
            """
            //div[@class="sys-line"]//a[contains(@href, "line-")]/@href
            """
        ).extract()
        for line in lines:
            yield Request(urljoin(response.url, line), self.initialize_locs)

    def initialize_locs(self, response):
        line_name = get_first(response.selector, '//div[@class="line-name"]/p/strong/text()')
        locations = response.xpath('//div[contains(@id, "_line")]')
        for location in locations:
            location_id = get_first(location, './@id')
            location_name = get_first(location, './div[1]/p/text()')
            location_id = "_".join(location_id.split('_')[:2])
            self.mapping[location_id] = {
                'line': line_name,
                'location': location_name
            }

    def parse(self, response):
        self.last_scrape = time.time()
        data = json.loads(response.body)
        for traffic_info in data:
            location_slug = "%d_%d" % (
                traffic_info[0][0],
                traffic_info[0][1]
            )
            location_data = self.mapping.get(location_slug, None)
            if location_data:
                iil = IntensityItemLoader()
                iil.add_value('name', location_data['location'])
                iil.add_value('line', location_data['line'])
                iil.add_value('mmda_line_id', traffic_info[0][0])
                iil.add_value('mmda_loc_id', traffic_info[0][1])

                north = IntensityItemLoader(iil.load_item())
                south = IntensityItemLoader(iil.load_item())
                north.add_value('direction', 'n')
                south.add_value('direction', 's')
                north.add_value('intensity', traffic_info[1][0])
                south.add_value('intensity', traffic_info[2][0])
                north.add_value(
                    'timestamp',
                    '%s-%s-%s %s:%s:%s +0800' % (
                        traffic_info[1][1][:4],
                        traffic_info[1][1][4:6],
                        traffic_info[1][1][6:8],
                        traffic_info[1][1][8:10],
                        traffic_info[1][1][10:12],
                        traffic_info[1][1][12:14]
                    )
                )
                south.add_value(
                    'timestamp',
                    '%s-%s-%s %s:%s:%s +0800' % (
                        traffic_info[2][1][:4],
                        traffic_info[2][1][4:6],
                        traffic_info[2][1][6:8],
                        traffic_info[2][1][8:10],
                        traffic_info[2][1][10:12],
                        traffic_info[2][1][12:14]
                    )
                )
                yield north.load_item()
                yield south.load_item()


    def scrape_traffic(self, spider):
        if time.time() - self.last_scrape >= 20:
            self.crawler.engine.schedule(
                Request('http://mmdatraffic.interaksyon.com/data.traffic.status.php', dont_filter=True),
                spider
            )
        raise DontCloseSpider


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
