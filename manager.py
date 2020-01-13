# -*- coding: utf-8 -*-
'''
@Date: 2020/1/6
@Author: fanyibin
@Description: 使用命令管理爬虫
'''
import re
from frame_library.logger import get_log_config
from seed.seed_manager import SeedManager
from config.config_parser import get_config
from importlib import import_module
from os import popen

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s', help='seed: to make start seeds')
parser.add_argument('-r', help='run: to run this spider')
parser.add_argument('-rs', help='restart: to restart this spider')
parser.add_argument('-c', help='clear: to clear all seeds of this spider')
parser.add_argument('-cd', help='clear dups: to clear all dups of this spider')
parser.add_argument('-v', help='view: to view this spider')
parser.add_argument('-k', help='kill: to kill the process for of this spider')
parser.add_argument('--runspider', help="Don't use this arg!")
args = parser.parse_args()


class Manager(object):
    def __init__(self):
        self.seed_name = args.s
        self.run_name = args.r
        self.clear_name = args.c
        self.cleardup_name = args.cd
        self.runspider_name = args.runspider
        self.view_name = args.v
        self.kill_name = args.k
        self.restart_name = args.rs

        self.name = (self.seed_name or self.run_name or self.clear_name or self.cleardup_name or self.runspider_name or
                     self.view_name or self.kill_name or self.restart_name)
        self.name_seed = ':'.join([self.name, 'seed'])
        self.name_dup = ':'.join([self.name, 'dup'])
        self.log = get_log_config(self.name)
        self.seedmanager = SeedManager()
        self.spider_config = get_config('spider_config.ini').get('SPIDERS', self.name)
        self.python_env = get_config('settings.ini').get('FRAME_SETTINGS', 'PYTHON_ENV')

    def _spider_conf(self):
        spider_conf = eval(self.spider_config)
        _file = spider_conf.get('file')
        _class = spider_conf.get('class')
        return _file, _class

    @property
    def _spider_inst(self):
        _file, _class = self._spider_conf()
        inst = getattr(import_module('spiders.%s' % _file), '%s' % _class)
        return inst()

    def _make_seeds(self):
        start_func = getattr(self._spider_inst, 'start_requests')()
        for seed in start_func:
            self.seedmanager.push_seed(self.name_seed, seed)

    def _run_spider(self):
        self._spider_inst.run_server()

    def _run_command(self):
        if self._check_spider_isalive():
            self.log.info('无法启动爬虫，因为爬虫已在后台运行，请使用 {} manager.py -rs {} 重启爬虫。'.format(
                self.python_env, self.name))
            return
        popen('nohup {} manager.py --runspider {} >/dev/null 2>&1 &'.format(self.python_env, self.name))
        self._view_spider()

    def _check_spider_isalive(self):
        if self._get_pid() is not None:
            return True
        return False

    def _clear_seeds(self):
        self.seedmanager.clear_seeds(self.name_seed)

    def _clear_dups(self):
        self.seedmanager.clear_dups(self.name_dup)

    def _get_pid_str(self, string):
        pid_str_lst = string.split(self.name)
        for _str in pid_str_lst:
            if 'runspider' in _str:
                return _str.strip()

    def _get_pid(self):
        ret = popen('ps -ef | grep {}'.format(self.name))
        str_ret = ret.read()
        if 'runspider' not in str_ret:
            return None
        pid_str = self._get_pid_str(str_ret)
        pid = re.search(r'\w+\s+(\d+)\s+', pid_str).group(1)
        return pid

    def _view_spider(self):
        _pid = self._get_pid()
        if _pid is None:
            return self.log.info('<{}>没有在后台运行，PID=None。'.format(self.name))
        self.log.info('<{}>正在后台运行，PID={}。'.format(self.name, _pid))
        return _pid

    def _kill_spider(self):
        _pid = self._get_pid()
        if _pid is None:
            return self.log.info('<{}>没有在后台运行，PID=None。'.format(self.name))
        popen('kill {}'.format(_pid))
        self.log.info('<{}>已停止运行，PID={}。'.format(self.name, _pid))

    def _restart_spider(self):
        self._kill_spider()
        self.log.info('爬虫准备重启...')
        self._run_command()

    def run(self):
        if self.clear_name:
            self._clear_seeds()
        if self.cleardup_name:
            self._clear_dups()
        if self.seed_name:
            self._make_seeds()
        if self.run_name:
            self._run_command()
        if self.runspider_name:
            self._run_spider()
        if self.view_name:
            self._view_spider()
        if self.kill_name:
            self._kill_spider()
        if self.restart_name:
            self._restart_spider()


if __name__ == '__main__':
    manager = Manager()
    manager.run()