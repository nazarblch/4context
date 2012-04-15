# Scrapy settings for ya_crawl project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'ya_crawl'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['ya_crawl.spiders']
NEWSPIDER_MODULE = 'ya_crawl.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

