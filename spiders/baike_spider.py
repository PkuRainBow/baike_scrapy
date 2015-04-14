from bs4 import BeautifulSoup
import re
import json
from urlparse import urlparse
import urllib

from scrapy.selector import Selector
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.contrib.spiders import CrawlSpider,Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle
from scrapy.http import Request

from baike.items import *
from misc.log import *

class baikeSpider(CrawlSpider):
	name = "baike"
	allowed_domains = ["baike.baidu.com"]
	domains = ["http://www.baike.baidu.com"]
	start_urls = [
		"http://www.baike.baidu.com/ziran",
		"http://www.baike.baidu.com/wenhua",
		"http://www.baike.baidu.com/dili",
		"http://www.baike.baidu.com/lishi",
		"http://www.baike.baidu.com/shenghuo",
		"http://www.baike.baidu.com/shehui",
		"http://www.baike.baidu.com/yishu",
		"http://www.baike.baidu.com/renwu",
		"http://www.baike.baidu.com/jingji",
		"http://www.baike.baidu.com/keji",
		"http://www.baike.baidu.com/tiyu",
	#	"http://www.baike.baidu.com/tese",
	]
        rules = [
		Rule(sle(allow=("/ziran$")),  callback='parse_top', follow=True),
		Rule(sle(allow=("/wenhua$")),  callback='parse_top',follow=True),
		Rule(sle(allow=("/dili$")),  callback='parse_top',  follow=True),
		Rule(sle(allow=("/lishi$")),  callback='parse_top', follow=True),
		Rule(sle(allow=("/shenghuo$")), callback='parse_top', follow=True),
		Rule(sle(allow=("/shehui$")), callback='parse_top', follow=True),
		Rule(sle(allow=("/yishu$")),  callback='parse_top', follow=True),
		Rule(sle(allow=("/renwu$")),  callback='parse_top', follow=True),
		Rule(sle(allow=("/jingji$")), callback='parse_top', follow=True),
		Rule(sle(allow=("/keji$")),   callback='parse_top', follow=True),
		Rule(sle(allow=("/tiyu$")),   callback='parse_top', follow=True),
		
		
		Rule(sle(allow=("/fenlei/.*$")),  callback='parse_view', follow=True),
		Rule(sle(allow=(".*limit=\d+&index=\d+&offset=\d+#gotoList$")),  callback='parse_view', follow=True),
		

		Rule(sle(allow=("/view/.*$")), callback='parse_word'),
		Rule(sle(allow=("/subview/.*$")), callback='parse_word'),
	#	Rule(sle(allow=("/subview/[0-9]*/.*$")), callback='parse', follow=True),
	]
 	
	def parse_word(self, response):
		info('parsed' + str(response))
		item = baikeItem()
	#	text = BeautifulSoup(response)
		sel = Selector(response)
		site = sel.css('head title')
		name = site.css('title::text').extract()
		label = sel.css('sapn::text').extract()
		item['name'] = name[0].split('_')[0]
   		item['url'] = response.url
		item['label'] = label[0]
	#	item['name'] = "".join(text.head.title)
	#	item['description'] = "".join(text.find_all("meta")[1])
   	#	item['url'] = response.url
	#	item['linkwords'] = "".join(text.find_all(href=re.compile("^/view/\d+.htm$")))
	#	item['name'] = text.css('title::text')[0].extract()
	#	item['description'] = text.css('meta[name=Discription]::attr(content)')[0].extract()
	#	item['linkwords'] = text.css('a[href*=/[view|subview]/]::text')[0].extract()
	#	items.append(item)
		return item

	def parse_top(self, response):
		info('parsed_top ' + str(response))
		items = []
		sel = Selector(response)
		sites = sel.css('span a[href*=fenlei]')
#		for site in sites:	
#			item = baikeSiteItem()
#			item['url'] = site.css('::attr(href)')[0].extract()
#			items.append(item)
#		return items		
		for site in sites:
			url = self.domains[0]+site.css('::attr(href)')[0].extract()[0]
			yield Request(url, callback=self.parse_view)
				
	def parse_view(self, response):
		info('parsed_view ' + str(response))
		items = []
		sel_view = Selector(response)
		sel_goto = Selector(response)
		sel_fenlei = Selector(response)
		sites_view = sel_view.css('li div a[href*=view]')
		sites_goto = sel_goto.css('a[href*=gotoList]')
		sites_fenlei = sel_fenlei.css('span a[href*=fenlei]')
		#for site in sites_view:	
		#	item = baikeSiteItem()
		#	item['url'] = site.css('::attr(href)')[0].extract()
		#	items.append(item)	
		#for site in sites_goto:	
		#	item = baikeSiteItem()
		#	item['url'] = site.css('::attr(href)')[0].extract()
		#	items.append(item)	
		#for site in sites_fenlei:
		#	item = baikeSiteItem()
		#	item['url'] = site.css('::attr(href)')[0].extract()
		#	items.append(item)
		for site in sites_view:	
			url = self.domains[0]+site.css('::attr(href)')[0].extract()[0]
			yield Request(url, callback=self.parse_word)
				
		for site in sites_goto:	
			url = self.domains[0]+site.css('::attr(href)')[0].extract()[0]
			yield Request(url, callback=self.parse_word)

		for site in sites_fenlei:
			url = self.domains[0]+site.css('::attr(href)')[0].extract()[0]
			yield Request(url, callback=self.parse_word)
