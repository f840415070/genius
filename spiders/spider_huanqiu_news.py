# -*- coding: utf-8 -*-
'''
@Date: 2020/1/13
@Author: fanyibin
@Description: 环球网新闻爬虫
'''
from core.genius import Genius
from frame_library.common_library import timestamp_to_timestr, get_content_from_html, check_image
import re


class HuanQiuNews(Genius):
    name = 'huanqiu_news'
    api_urls = {
        'china': 'https://china.huanqiu.com/api/list2?node={}&offset={}&limit=20',
        'world': 'https://world.huanqiu.com/api/list2?node={}&offset={}&limit=20',
        'mil': 'https://mil.huanqiu.com/api/list2?node={}&offset={}&limit=20',
        'finance': 'https://finance.huanqiu.com/api/list2?node={}&offset={}&limit=20',
        'tech': 'https://tech.huanqiu.com/api/list2?node={}&offset={}&limit=20',
        'culture': 'https://cul.huanqiu.com/api/list2?node={}&offset={}&limit=20',
    }
    api_nodes = {
        'china': ['/e3pmh1nnq/e7tl4e309', '/e3pmh1nnq/e3pra70uk', '/e3pmh1nnq/e3pn61c2g'],
        'world': ['/e3pmh22ph/e3pmh26vv', '/e3pmh22ph/e3pmh2398', '/e3pmh22ph/e3pn62kms'],
        'mil': ['/e3pmh1dm8/e3pmt7hva', '/e3pmh1dm8/e3pn62l96', '/e3pmh1dm8/e3pmtdr2r'],
        'finance': ['/e3pmh1hmp/e3pmh28kq', '/e3pmh1hmp/e3pmh1pvu', '/e3pmh1hmp/e3pn61chp'],
        'tech': ['/e3pmh164r/e3pmtm015', '/e3pmh164r/e3pmh33i9', '/e3pmh164r/e3pmtmdvg', '/e3pmh164r/e3pmtnh4j',
                 '/e3pmh164r/e3pn46ri0', '/e3pmh164r/e3pmh3dh4', '/e3pmh164r/e3pmtlao3', '/e3pmh164r/e3pmh356p',
                 '/e3pmh164r/e3pmh2hq8', '/e3pmh164r/e3ptqlvrg'],
        'culture': ['/e3pn677q4/e7n7nshou', '/e3pn677q4/e7n7nshou/e7n7o5sgv', '/e3pn677q4/e7n7nshou/e7n7oj8js',
                    '/e3pn677q4/e7n7nshou/e7n7opklk', '/e3pn677q4/e7n7nshou/e80schtc2']
    }
    offsets = [i * 20 for i in range(20)]

    def start_requests(self):
        for classify, url in self.api_urls.items():
            for node in self.api_nodes[classify]:
                for offset in self.offsets:
                    yield self.seeding(url.format(node, offset), self.parse_api_list, meta=classify)

    def parse_api_list(self, response):
        resp = response.json
        news_list = resp['list'][:-1]
        for each in news_list:
            url_prefix = re.search(r'^(.*?com)', response.response.url).group(1)
            url = url_prefix + '/article/' + each['aid']
            if self.filter_item(url):
                item = {}
                item['url'] = url
                item['title'] = each['title']
                item['source'] = each['source']['name']
                item['publish_timestamp'] = int(each['ctime'])
                item['publish_timestr'] = timestamp_to_timestr(int(item['publish_timestamp']/1000))
                item['web_source'] = '环球网'
                item['classify'] = response.meta
                cover = each['cover']
                item['cover'] = cover if 'http' in cover else 'https:' + cover
                item['keywords'] = []
                yield self.seeding(url, self.parse_article, meta=item)

    def parse_article(self, response):
        item = response.meta
        resp = response.etree_html
        content_ = get_content_from_html(resp, "//article", 'a', 'strong', 'em')
        if content_ is None:
            return self.log.info('html未提取到内容，故放弃本次请求。')
        item['content_html'] = content_[0]
        item['content_text'] = content_[1]
        item['images'] = []
        images_ = content_[2]
        for img in images_:
            if 'http' not in img:
                img = 'https:' + img
            if not check_image(img):
                continue
            item['images'].append(img)
        item['article_type'] = 2 if item['images'] else 1
        self.save_to_mongo(item)


if __name__ == '__main__':
    huanqiu = HuanQiuNews()
    huanqiu.run(start_seeds=True)
