# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#import redis
from datetime import datetime
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
from hashlib import md5
from scrapy import log


import json
import codecs
#import MySQLdb
from collections import OrderedDict


class JsonWithEncodingPipeline(object):

    def __init__(self):
        self.file = codecs.open('data_utf8.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(OrderedDict(item), ensure_ascii=False, sort_keys=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MySQLStorePipeline(object):
	def __init__(self, dbpool):
		self.dbpool = dbpool

	@classmethod
	def from_settings(cls, settings):
		dbargs = dict(
			host=settings['MYSQL_HOST'],
			db=settings['MYSQL_DBNAME'],
			user=settings['MYSQL_USER'],
			passwd=settings['MYSQL_PASSWD'],
			charset='utf8',
			use_unicode=True,
		)
		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
		return cls(dbpool)

	def process_item(self, item, spider):
		d = self.dbpool.runInteraction(self._do_upsert, item, spider);
		d.addErrback(self._handle_error, item, spider);
		d.addBoth(lambda _: item)
		return d

	def _do_upsert(self, conn, item, spider):
		guid = self._get_guid(item)
		now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
		conn.execute("""SELECT EXISTS(
			SELECT 1 FROM scrapy_baike WHERE guid = %s
		)""", (guid, ))
		ret = conn.fetchone()[0]

		if ret:
			conn.execute("""
				UPDATE scrapy_baike 
				SET name=%s, label=%s, url=%s, updated=%s
				WHERE guid=%s
			""", (item['name'], item['label'], item['url'], now, guid))
			spider.log("Item updated in db: %s %r" % (guid, item))
		else:
			conn.execute("""
				INSERT INTO scrapy_baike (guid, name, label, url, updated)
				VALUES (%s, %s, %s, %s, %s)
			""", (guid, item['name'], item['label'], item['url'], now))
			spider.log("Item stored in db: %s %r" % (guid, item))

	def	_handle_error(self, failure, item, spider):
		log.err(failure)

	def _get_guid(self, item):
		return md5(item['url']).hexdigest()

