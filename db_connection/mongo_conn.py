# -*- coding: utf-8 -*-
'''
@Date: 2019/12/26
@Author: fanyibin
@Description: None
'''
from config.config_parser import get_config
from frame_library.singleton import Singleton
from pymongo import MongoClient


class MongoConn(metaclass=Singleton):
    def __init__(self):
        self.debug_cfg = get_config('settings.ini')
        self.debug = self.debug_cfg.getboolean('MODE', 'DEBUG')
        self.config = get_config('debug_config.ini' if self.debug else 'server_config.ini')
        self.host = self.config.get('MONGO', 'HOST')
        self.port = self.config.getint('MONGO', 'PORT')
        self.db = self.config.get('MONGO', 'DB')
        self.username = self.config.get('MONGO', 'USERNAME')
        self.password = self.config.get('MONGO', 'PASSWORD')
        self._client = MongoClient(self.host, self.port)
        self.db = self._client[self.db]
        if all([self.username, self.password]):
            self.db.authenticate(self.username, self.password)

    @property
    def get_db(self):
        return self.db


if __name__ == '__main__':
    conn = MongoConn()
    db = conn.get_db
    col = db['cctv_news']
    r = col.find_one()
    print(r)
