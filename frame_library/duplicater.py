# -*- coding: utf-8 -*-
'''
@Date: 2019/12/26
@Author: fanyibin
@Description: None
'''
from db_connection.redis_conn import RedisConn
from frame_library.logger import get_log_config
import hashlib


class Duplicater(object):
    def __init__(self):
        self.client = RedisConn().get_client
        self.log = get_log_config()

    def _make_md5(self, item):
        return hashlib.md5(item.encode()).hexdigest()

    def duplicate(self, name, item):
        result = self.client.sadd(name, self._make_md5(item))
        if not result:
            self.log.info('已被去重：{}'.format(item))
        return result
