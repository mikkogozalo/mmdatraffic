# -*- coding: utf-8 -*-

# Scrapy settings for mmdatraffic project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'mmdatraffic'

SPIDER_MODULES = ['mmdatraffic.spiders']
NEWSPIDER_MODULE = 'mmdatraffic.spiders'
ITEM_PIPELINES = {
    'mmdatraffic.pipelines.LatestPipeline': 100,
    # 'mmdatraffic.pipelines.MySQLPipeline': 150,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mmdatraffic (+http://www.yourdomain.com)'
