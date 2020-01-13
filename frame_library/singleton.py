# -*- coding: utf-8 -*-
'''
@Date: 2019/12/14
@Author: fanyibin
@Description: None
'''

class Singleton(type):
    _instance = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instance:
            self._instance[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instance[self]


class TestOne(metaclass=Singleton):
    pass


if __name__ == '__main__':
    t1 = TestOne()
    t2 = TestOne()
    print(id(t1))
    print(id(t2))