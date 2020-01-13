# -*- coding: utf-8 -*-
'''
@Date: 2019/12/30
@Author: fanyibin
@Description: 响应中间件
'''
from frame_library.singleton import Singleton
from frame_library.logger import get_log_config


class ResMiddleware(metaclass=Singleton):
    def __init__(self):
        self.log = get_log_config()

    def check_response(self, res):
        if not res:
            self.log.warning('响应体为空，无法解析。将执行下一条种子。')
            return None
        return res

    def handle_response(self, res, seed):
        resp = self.check_response(res)
        if resp is None:
            return resp
        if seed.encoding is None:
            seed.encoding = 'utf-8'
        resp.encoding = seed.encoding
        resp.close()
        return resp