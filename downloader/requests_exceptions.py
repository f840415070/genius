# -*- coding: utf-8 -*-
'''
@Date: 2019/12/27
@Author: fanyibin
@Description: requests 异常汇总
'''
from frame_library.singleton import Singleton
from requests import exceptions as ex
from copy import deepcopy


class ReqExceptions(metaclass=Singleton):
    # TODO: 再细分异常并给出解决方案

    def __init__(self):
        self.ConnectTimeout = ex.ConnectTimeout
        self.HTTPError = ex.HTTPError
        self.ConnectionError = ex.ConnectionError
        self.ProxyError = ex.ProxyError
        self.SSLError = ex.SSLError
        self.Timeout = ex.Timeout
        self.ReadTimeout = ex.ReadTimeout
        self.URLRequired = ex.URLRequired
        self.TooManyRedirects = ex.TooManyRedirects
        self.MissingSchema = ex.MissingSchema
        self.InvalidSchema = ex.InvalidSchema
        self.InvalidURL = ex.InvalidURL
        self.InvalidHeader = ex.InvalidHeader
        self.ChunkedEncodingError = ex.ChunkedEncodingError
        self.ContentDecodingError = ex.ContentDecodingError
        self.StreamConsumedError = ex.StreamConsumedError
        self.RetryError = ex.RetryError
        self.UnrewindableBodyError = ex.UnrewindableBodyError

    def get_timeout_errors(self):
        return self.ConnectTimeout, self.Timeout, self.ReadTimeout

    def get_other_request_errors(self):
        errors = deepcopy(self.__dict__)
        for e in ('ConnectTimeout', 'Timeout', 'ReadTimeout'):
            errors.pop(e)
        return tuple(errors.values())


if __name__ == '__main__':
    reqex = ReqExceptions()
    print(reqex.get_other_request_errors())
