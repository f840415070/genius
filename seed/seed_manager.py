# -*- coding: utf-8 -*-
'''
@Date: 2019/12/19
@Author: fanyibin
@Description: None
'''
from db_connection.redis_conn import RedisConn
from frame_library.logger import get_log_config
from seed.seed import Seed
from middlewares.spider_middleware import SpiderMiddleware
import json


class SeedManager(object):

    def __init__(self):
        self.client = RedisConn().get_client
        self.log = get_log_config('SeedManager')
        self.spidermiddleware = SpiderMiddleware()

    def push_seed(self, keyname, seed):
        _seed = self.spidermiddleware.handle_seed(seed, keyname)
        if _seed is not None:
            this_seed = json.dumps(_seed.get_seed_dict())
            self.client.rpush(keyname, this_seed)
            self.log.info('往<{}>存入一条种子，指定解析函数为<{}>；当前种子数量：{}。'.format(
                keyname, seed.parse_func, self.get_seed_count(keyname)))

    def pop_seed(self, keyname):
        this_seed = self.client.rpop(keyname)
        if this_seed is None:
            return this_seed
        seed_dict = json.loads(this_seed)
        seed = Seed(**seed_dict)
        self.log.info('从<{}>取出一条种子，指定解析函数为<{}>；当前种子数量：{}。'.format(
            keyname, seed.parse_func, self.get_seed_count(keyname)))
        return seed

    def clear_seeds(self, keyname):
        self.client.delete(keyname)
        self.log.info('已清空<{}>所有种子。'.format(keyname))

    def clear_dups(self, keyname):
        self.client.delete(keyname)
        self.log.info('已清空<{}>所有去重记录。'.format(keyname))

    def get_seed_count(self, keyname):
        return self.client.llen(keyname)


if __name__ == '__main__':
    mng = SeedManager()

