# -*- coding: utf-8 -*-
'''
@Date: 2020/1/2
@Author: fanyibin
@Description: None
'''
from db_connection.mongo_conn import MongoConn
from frame_library.singleton import Singleton
from middlewares.spider_middleware import SpiderMiddleware
from frame_library.logger import get_log_config


class MongoPipe(metaclass=Singleton):
    def __init__(self):
        self.log = get_log_config()
        self.mongoconn = MongoConn()
        self.client = self.mongoconn.get_client
        self.spidermiddleware = SpiderMiddleware()

    def save_item(self, collection, item):
        _item = self.spidermiddleware.handle_item(item, collection)
        if _item is None:
            return 0
        self.client[self.mongoconn.db][collection].insert_one(_item)
        self.log.info('已保存一条数据至MongoDB。')
        return 1