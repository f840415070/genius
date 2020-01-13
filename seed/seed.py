# -*- coding: utf-8 -*-
'''
@Date: 2019/12/14
@Author: fanyibin
@Description: None
'''
from lxml import etree


class Seed(object):
    _kwargs_keys = ['timeout', 'verify', 'stream', 'cert', 'allow_redirects',
                    'files', 'json', 'auth', 'hooks', 'proxies']

    def __init__(self, url, parse_func,
                 method=None, data=None, params=None, cookies=None, headers=None, meta=None, encoding=None,
                 filter_item=None, **kwargs):
        self.url = url
        self.parse_func = parse_func
        self.method = method
        self.data = data
        self.params = params
        self.cookies = cookies
        self.headers = headers
        self.meta = meta
        self.encoding = encoding
        self.filter_item = filter_item

        for key in kwargs.keys():
            if key in self._kwargs_keys:
                setattr(self, key, kwargs[key])

    @property
    def text(self):
        return self.response.text

    @property
    def json(self):
        return self.response.json()

    @property
    def etree_html(self):
        return etree.HTML(self.text)

    @property
    def content(self):
        return self.response.content

    def get_seed_dict(self):
        seed_dict = self.__dict__
        if not isinstance(seed_dict.get('parse_func'), str):
            seed_dict['parse_func'] = seed_dict.get('parse_func').__name__
        return seed_dict