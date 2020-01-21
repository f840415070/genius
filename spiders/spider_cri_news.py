# -*- coding: utf-8 -*-
'''
@Date: 2020/1/21
@Author: fanyibin
@Description: 国际在线新闻爬虫
'''
from core.genius import Genius
from frame_library.common_library import timestr_to_timestamp, get_content_from_html, check_image
import json
import re


class SpiderCriNews(Genius):
    name = 'cri_news'
    url = 'http://news.cri.cn/world'

    def start_requests(self):
        yield self.seeding(self.url, self.parse_list)

    def parse_list(self, response):
        res = response.etree_html
        dateurls = json.loads(res.xpath("//ul[@class='more-wrap']/@dateurls")[0])
        urls = dateurls['urls']
        for url_ in urls:
            yield self.seeding('http://news.cri.cn' + url_, self.parse_detail_list)

    def parse_detail_list(self, response):
        res = response.etree_html
        page_list = res.xpath("//ul/li")
        for this_news in page_list:
            item = {}
            url = 'http://news.cri.cn' + this_news.xpath(".//div[@class='list-title']/a/@href")[0]
            if self.filter_item(url):
                item['url'] = url
                item['title'] = this_news.xpath(".//div[@class='list-title']/a/text()")[0]
                item['cover'] = 'http:' + this_news.xpath(".//img/@src")[0]
                time_text = this_news.xpath(".//div[@class='list-time']/text()")[0]
                timestr = re.sub('[年月]', '-', time_text.replace('日', ''))
                item['publish_timestr'] = timestr
                item['publish_timestamp'] = timestr_to_timestamp(timestr)
                item['web_source'] = '国际在线'
                item['classify'] = 'world'
                yield self.seeding(url, 'parse_article', meta=item)

    def parse_article(self, response):
        item = response.meta
        resp = response.etree_html
        content_ = get_content_from_html(resp, "//div[@id='abody']", 'a', 'strong', 'em')
        if content_ is None:
            return self.log.info('html未提取到内容，故放弃本次请求。')
        item['content_html'] = content_[0]
        item['content_text'] = content_[1]
        item['images'] = []
        images_ = content_[2]
        for img in images_:
            if 'http' not in img:
                img = 'http:' + img
            if not check_image(img):
                continue
            item['images'].append(img)
        item['article_type'] = 2 if item['images'] else 1

        try:
            source = resp.xpath("//span[@id='asource']/a/text()")[0]
        except IndexError:
            source_str = resp.xpath("//span[@id='asource']/text()")[0]
            source = re.search(r'来源：(.*?)$', source_str).group(1)
        item['source'] = source
        item['keywords'] = []
        self.save_to_mongo(item)


if __name__ == '__main__':
    cri = SpiderCriNews()
    cri.run(start_seeds=True)