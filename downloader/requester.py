# -*- coding: utf-8 -*-
'''
@Date: 2019/12/14
@Author: fanyibin
@Description: None
'''
from requests import Session, Request, packages
packages.urllib3.disable_warnings()
from frame_library.logger import get_log_config
from middlewares.request_middleware import ReqMiddleware
from middlewares.response_middleware import ResMiddleware
from downloader.requests_exceptions import ReqExceptions
import time
import traceback


class Requester(object):
    def __init__(self):
        self.log = get_log_config()
        self.session = Session()
        self.reqmiddleware = ReqMiddleware()
        self.resmiddleware = ResMiddleware()
        self.req_ex = ReqExceptions()
        self.timeout_errors = self.req_ex.get_timeout_errors()
        self.other_request_errors = self.req_ex.get_other_request_errors()

    def reqsend(self, seed):
        req_kwargs = self.reqmiddleware.handle_request(seed)
        request = self.session.prepare_request(Request(**req_kwargs))
        send_kwargs = self.reqmiddleware.make_send_kwargs(seed)
        self.log.info('开始请求：{}'.format(seed.url))
        if send_kwargs.get('proxies'):
            self.log.info('使用代理：{}'.format([i for i in send_kwargs['proxies'].values()][0]))
        ctime = time.time()
        res = self.session.send(request, **send_kwargs)
        self.log.info('获得响应，请求时长：{}s。'.format(round(time.time() - ctime, 3)))
        resp = self.resmiddleware.handle_response(res, seed)
        return resp

    def get_response(self, seed):
        """发送请求，获取响应，连接超时将重试3次"""
        _retry = 0
        while True:
            try:
                response = self.reqsend(seed)
                return response
            except self.timeout_errors:
                _retry += 1
                if _retry > 3:
                    break
                self.log.warning('连接超时，等待5s后重试...')
                time.sleep(5)
                self.log.info('重试第{}次...'.format(_retry))
            except self.other_request_errors:
                self.log.warning('请求发生错误！异常追踪如下：')
                self.log.error(traceback.format_exc())
                break

        self.log.warning('请求出现了错误，无法获得响应，即将忽略此请求并执行下一条种子。')
        return None
