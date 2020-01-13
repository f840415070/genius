# -*- coding: utf-8 -*-
'''
@Date: 2019/12/14
@Author: fanyibin
@Description: None
'''
import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from frame_library.singleton import Singleton
from config.config_parser import get_config


class Logger(metaclass=Singleton):
    def __init__(self, name):
        self.config = get_config('settings.ini')
        self.LOG_ENABLED = self.config.getboolean('LOG', 'LOG_ENABLED')
        self.LOG_TO_CONSOLE = self.config.getboolean('LOG', 'LOG_TO_CONSOLE')
        self.LOG_TO_FILE = self.config.getboolean('LOG', 'LOG_TO_FILE')
        self.LOG_LEVEL = self.config.get('LOG', 'LOG_LEVEL')
        self.LOG_FORMAT = self.config.get('LOG', 'LOG_FORMAT')
        self.LOG_PATH = self.config.get('LOG', 'LOG_PATH')

        self.name = name
        self.logger = logging.getLogger(name=self.name)
        self.logger.setLevel(self.LOG_LEVEL)

        self.log_to_console()
        self.log_to_file()
        self.logger.propagate = False

    def check_path(self):
        if not os.path.exists(self.LOG_PATH):
            raise FileNotFoundError("找不到log文件夹，请在 /Genius/config/settings.ini LOG_PATH 检查或修改路径。")

    def log_to_console(self):
        # 输出到控制台
        if self.LOG_ENABLED and self.LOG_TO_CONSOLE:
            stream_handler = logging.StreamHandler(sys.stderr)
            stream_handler.setLevel(self.LOG_LEVEL)
            formatter = logging.Formatter(self.LOG_FORMAT)
            stream_handler.setFormatter(formatter)
            return self.logger.addHandler(stream_handler)

    def log_to_file(self):
        # 输出到文件
        if self.LOG_ENABLED and self.LOG_TO_FILE:
            self.check_path()
            filename = os.path.join(self.LOG_PATH, ''.join([self.name, '.log']))
            file_handler = TimedRotatingFileHandler(filename=filename, when='D', backupCount=3,
                                                    interval=1, encoding='utf-8')
            file_handler.setLevel(self.LOG_LEVEL)
            formatter = logging.Formatter(self.LOG_FORMAT)
            file_handler.setFormatter(formatter)
            return self.logger.addHandler(file_handler)


def get_log_config(name=None):
    logger_ = Logger(name)
    return logger_.logger


if __name__ == '__main__':
    log = get_log_config(name='mylog')
    log.debug('this is debug log')
    log.info('this is info log')
    log.warning('this is warning log')
    log.error('this is error log')