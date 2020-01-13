# -*- coding: utf-8 -*-
'''
@Date: 2019/12/14
@Author: fanyibin
@Description: None
'''
from core.genius import Genius


class SpiderDemo(Genius):
    name = 'demo'
    url = 'http://www.baidu.com'

    def start_requests(self):
        yield self.seeding(self.url, self.parse, meta={'greet': 'hello world'})

    def parse(self, response):
        item = response.meta
        self.save_to_mongo(item)


if __name__ == '__main__':
    demo = SpiderDemo()
    demo.run(start_seeds=True)
