# -*- coding: utf-8 -*-
'''
@Date: 2019/12/26
@Author: fanyibin
@Description: None
'''
from config.config_parser import get_config
from frame_library.singleton import Singleton
from pymongo import MongoClient
from urllib.parse import quote_plus


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

        self.uri = self.get_uri()
        self._client = MongoClient(self.uri)

    def get_uri(self):
        if self.debug:
            uri = 'mongodb://{}:{}/{}'.format(self.host, self.port, self.db)
        else:
            if not all([self.username, self.password]):
                uri = 'mongodb://{}:{}/{}'.format(self.host, self.port, self.db)
            else:
                uri = 'mongodb://{}:{}@{}:{}/{}'.format(
                    quote_plus(self.username), quote_plus(self.password), self.host, self.port, self.db
                )
        return uri

    @property
    def get_client(self):
        return self._client


if __name__ == '__main__':
    client = MongoConn()
    print(client.uri)
    col = client._client['TechNews']['cctv_tech']
    r = col.find_one({'_id': 'ARTIYGnL0WqPO2ZdwKcdTjo8191119'})
    print(r)
