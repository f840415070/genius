# -*- coding: utf-8 -*-
'''
@Date: 2020/1/10
@Author: fanyibin
@Description: 央视网新闻爬虫
'''
from core.genius import Genius
from frame_library.common_library import timestr_to_timestamp, get_content_from_html
import re


class SpiderCctvNews(Genius):
    name = 'cctv_news'

    news_type = ('china', 'world', 'society', 'law', 'ent', 'tech', 'life')
    api_url = 'http://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/{}_{}.jsonp?cb=t&cb={}'
    type_map = {'jingji': 'finance', 'military': 'mil'}
    old_api_url = 'http://{}.cctv.com/data/index.json'

    def start_requests(self):
        for _type in self.news_type:
            for page in range(1, 8):
                url = self.api_url.format(_type, page, _type)
                yield self.seeding(url, self.parse_api_list, meta=_type)

        for t, t_ in self.type_map.items():
            yield self.seeding(self.old_api_url.format(t), self.parse_old_api_list, meta=t_)

    def parse_api_list(self, response):
        listnews = re.search(r'"list":(.*?)}}\)', response.text).group(1)
        allnews = re.findall(r'({.*?})', listnews)
        for news in allnews:
            _news = eval(news)
            url = _news['url']
            if self.filter_item(url):
                item = {}
                item['url'] = url
                item['title'] = _news['title']
                item['classify'] = response.meta
                item['publish_timestr'] = _news['focus_date']
                item['publish_timestamp'] = timestr_to_timestamp(item['publish_timestr'])
                item['cover'] = _news['image']
                item['keywords'] = _news['keywords'].split(' ')
                item['web_source'] = '央视网'
                yield self.seeding(url, self.parse_article, meta=item)

    def parse_old_api_list(self, response):
        resp = response.json
        for news in resp['rollData']:
            url = news['url']
            if self.filter_item(url):
                item = {}
                item['url'] = url
                item['title'] = news['title']
                item['classify'] = response.meta
                item['publish_timestr'] = news['dateTime']
                item['publish_timestamp'] = timestr_to_timestamp(item['publish_timestr'])
                item['cover'] = news['image']
                item['keywords'] = news['content'].split(' ')
                item['web_source'] = '央视网'
                yield self.seeding(url, self.parse_article, meta=item)

    def parse_article(self, response):
        item = response.meta
        resp = response.etree_html
        if resp.xpath("//meta[@name='spm-id']"):
            content_ = get_content_from_html(resp, "//div[@class='content_area']", 'a', 'strong')
            if content_ is None:
                return self.log.info('html未提取到内容，故放弃本次请求。')
        else:
            content_ = get_content_from_html(resp, "//div[@class='cnt_bd']", 'a', 'strong')
            if content_ is None:
                return self.log.info('html未提取到内容，故放弃本次请求。')

        item['content_html'] = content_[0]
        item['content_text'] = content_[1]
        item['images'] = []
        images_ = content_[2]
        for img in images_:
            if 'erweima' in img:
                continue
            if 'http' not in img:
                img = 'http:' + img
            item['images'].append(img)
        item['article_type'] = 2 if item['images'] else 1
        source = resp.xpath("//meta[@name='source']/@content")
        item['source'] = source[0] if source else '央视网'
        self.save_to_mongo(item)


if __name__ == '__main__':
    cctv = SpiderCctvNews()
    cctv.run(start_seeds=True)
