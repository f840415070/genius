# -*- coding: utf-8 -*-
'''
@Date: 2020/1/8
@Author: fanyibin
@Description: 管理所有爬虫
'''
from config.config_parser import get_config
from os import popen
from multiprocessing import Process

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--view', help="--view all: view all spiders")
parser.add_argument('--kill', help="--kill all: kill all spiders")
parser.add_argument('--restart', help="--restart all: restart all spiders")
args = parser.parse_args()


class AllManager(object):
    env = get_config('settings.ini').get('FRAME_SETTINGS', 'PYTHON_ENV')
    names = get_config('spider_config.ini').options('SPIDERS')
    arg_command_map = {
        'view': '{} manager.py -v {}',
        'kill': '{} manager.py -k {}',
        'restart': '{} manager.py -rs {}',
    }

    def __init__(self):
        self.arg_inst = self._get_arg_key()

    def _get_arg_key(self):
        arg_kwargs = args._get_kwargs()
        for group in arg_kwargs:
            if group[1] == 'all':
                arg_inst = group[0]
                return arg_inst

    def _get_command(self, arg, name):
        return self.arg_command_map[arg].format(self.env, name)

    def run(self):
        _task = [Process(target=self._execute_command, args=(name,)) for name in self.names]
        for item_task in _task:
            item_task.start()
        del _task
        return

    def _execute_command(self, name):
        popen(self._get_command(self.arg_inst, name))


if __name__ == '__main__':
    man = AllManager()
    man.run()
