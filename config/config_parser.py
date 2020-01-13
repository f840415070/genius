# -*- coding: utf-8 -*-
'''
@Date: 2019/12/19
@Author: fanyibin
@Description: None
'''
from configparser import RawConfigParser
from frame_library.singleton import Singleton
import os


class LoadConfig(metaclass=Singleton):
    def __init__(self):
        self.cfg = RawConfigParser()
        self._path = os.path.dirname(os.path.abspath(__file__))

    def load_config(self, cfg_file):
        self.cfg.read(os.path.join(self._path, cfg_file), encoding='utf-8')
        return self.cfg


def get_config(config_file):
    config = LoadConfig().load_config(config_file)
    return config


if __name__ == '__main__':
    config = get_config('spider_scheduler_config.ini')
    content = config.get('SEED_SCHEDULE', 'demo')
    content = eval(content)
    print(content)
    print(type(content))
