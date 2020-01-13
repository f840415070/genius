# -*- coding: utf-8 -*-
'''
@Date: 2019/12/30
@Author: fanyibin
@Description: 请求中间件
'''
from frame_library.singleton import Singleton
from downloader.user_agent_pool import UserAgent_POOL
import random


class ReqMiddleware(metaclass=Singleton):
    # TODO: ADD PROXIES
    default_method = 'GET'
    default_timeout =  10
    default_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Upgrade-Insecure-Requests": "1",
            }

    def __init__(self):
        self.UserAgentPool = UserAgent_POOL

    def check_request(self):
        pass

    def handle_request(self, seed):
        if seed.headers is None:
            seed.headers = self.default_headers
        if not seed.headers.get('User-Agent'):
            seed.headers['User-Agent'] = random.choice(self.UserAgentPool)
        if not seed.method:
            seed.method = self.default_method

        req_kwargs = {'method': seed.method.upper(), 'headers': seed.headers, 'url': seed.url,
                      'data': seed.data, 'params': seed.params, 'cookies': seed.cookies}
        _kwargs = {
            'files': getattr(seed, 'files') if hasattr(seed, 'files') else None,
            'json': getattr(seed, 'json') if hasattr(seed, 'json') else None,
            'auth': getattr(seed, 'auth') if hasattr(seed, 'auth') else None,
            'hooks': getattr(seed, 'hooks') if hasattr(seed, 'hooks') else None,
        }
        req_kwargs.update(_kwargs)
        return req_kwargs

    def get_proxies(self):
        proxies = {}
        return proxies

    def make_send_kwargs(self, seed):
        send_kwargs = {
            'timeout': getattr(seed, 'timeout') if hasattr(seed, 'timeout') else self.default_timeout,
            'verify': getattr(seed, 'verify') if hasattr(seed, 'verify') else True,
            'stream': getattr(seed, 'stream') if hasattr(seed, 'stream') else False,
            'cert': getattr(seed, 'cert') if hasattr(seed, 'cert') else None,
            'allow_redirects': getattr(seed, 'allow_redirects') if hasattr(seed, 'allow_redirects') else True,
            'proxies': getattr(seed, 'proxies') if hasattr(seed, 'proxies') else None
        }
        proxies = self.get_proxies()
        if send_kwargs.get('proxies') is None and proxies:
            send_kwargs.update({'proxies': proxies})
        return send_kwargs