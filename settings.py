# -*- coding: utf-8 -*-

# Scrapy settings for baike project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import sys
import os
from os.path import dirname
path = dirname(dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(path)
from misc.log import *

BOT_NAME = 'baike'

SPIDER_MODULES = ['baike.spiders']
NEWSPIDER_MODULE = 'baike.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'baike (+http://www.yourdomain.com)'

DOWNLODAER_MIDDLEWARES = {
	'misc.middleware.CustomUserAgentMiddleware':401,
}

ITEM_PIPELINES = {
	'baike.pipelines.JsonWithEncodingPipeline':300,
}

LOG_LEVEL = 'INFO'

DOWNLOAD_DELAY = 1
