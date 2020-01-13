# -*- coding: utf-8 -*-
'''
@Date: 2019/12/24
@Author: fanyibin
@Description: None
'''
import redis
from frame_library.singleton import Singleton
from config.config_parser import get_config


class RedisConn(metaclass=Singleton):
    def __init__(self):
        self.debug_cfg = get_config('settings.ini')
        self.debug = self.debug_cfg.getboolean('MODE', 'DEBUG')
        self.config = get_config('debug_config.ini' if self.debug else 'server_config.ini')
        self.host = self.config.get('REDIS', 'HOST')
        self.port = self.config.get('REDIS', 'PORT')
        self.db = self.config.getint('REDIS', 'DB')
        self.password = self.config.get('REDIS', 'PASSWORD')
        self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password)
        self.client = redis.StrictRedis(connection_pool=self.pool)

    @property
    def get_client(self):
        return self.client


if __name__ == '__main__':
    client = RedisConn().get_client
    print(client)