# -*- coding: utf-8 -*-
'''
@Date: 2020/3/18
@Author: fanyibin
@Description: None
'''
from core.genius import Genius


class HotNews(Genius):
    name = 'hot_news'

    huanqiu_urls = [
        'https://world.huanqiu.com/',
        'https://china.huanqiu.com/',
        'https://mil.huanqiu.com/',
        'https://tech.huanqiu.com/'
    ]

    chinanews_url = 'http://www.chinanews.com/importnews.html'

    def start_requests(self):
        for url in self.huanqiu_urls:
            yield self.seeding(url, 'parse_huanqiu')
        yield self.seeding(self.chinanews_url, 'parse_chinanews')

    def parse_huanqiu(self, res):
        resp = res.etree_html
        news_list = resp.xpath("//div[@class='r-container']/div[2]//ul/li")
        for i in news_list:
            item = {}
            item['url'] = 'https:' + i.xpath("./a/@href")[0]
            item['title'] = i.xpath(".//p/text()")[0]
            item['source'] = '环球网'
            item['has_marked'] = 0
            if self.filter_item(item['url']):
                self.save_to_mongo(item)

    def parse_chinanews(self, res):
        resp = res.etree_html
        news_list = resp.xpath("//div[@class='content_list']/ul/li")
        for each in news_list:
            hascon = each.xpath("./div[@class='dd_bt']")
            if hascon:
                url = each.xpath("./div[@class='dd_bt']/a[last()]/@href")[0]
                if self.filter_item(url) or 'shipin' in url:
                    item = {}
                    item['url'] = url
                    title = each.xpath("./div[@class='dd_bt']/a[last()]/text()")
                    if not title:
                        continue
                    item['title'] = title[0]
                    item['source'] = '中国新闻网'
                    item['has_marked'] = 0
                    if self.filter_item(item['url']):
                        self.save_to_mongo(item)


if __name__ == '__main__':
    spider = HotNews()
    spider.run(start_seeds=True, clear_dups=True)
