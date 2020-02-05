# -*- coding: utf-8 -*-
'''
@Date: 2020/2/3
@Author: fanyibin
@Description: 中国新闻网爬虫
'''
from core.genius import Genius
from frame_library.common_library import timestr_to_timestamp, get_content_from_html, check_image


class SpiderChinaNews(Genius):
    name = 'china_news'
    urls = ['http://www.chinanews.com/scroll-news/news{}.html'.format(i) for i in range(1, 11)]
    classify_tag = ('社会', '国内', '国际', '财经', '文化', '娱乐', '体育')
    classify_map = {'社会': 'society', '国内': 'china', '国际': 'world', '财经': 'finance',
                    '文化': 'culture', '娱乐': 'ent', '体育': 'sports'}

    def start_requests(self):
        for url in self.urls:
            yield self.seeding(url, self.parse_list)

    def parse_list(self, response):
        resp = response.etree_html
        news_list = resp.xpath("//div[@class='content_list']/ul/li")
        for each in news_list:
            hascon = each.xpath("./div[@class='dd_bt']")
            if hascon:
                url = 'http:' + each.xpath("./div[@class='dd_bt']/a/@href")[0]
                if self.filter_item(url):
                    item = {}
                    item['url'] = url
                    item['title'] = each.xpath("./div[@class='dd_bt']/a/text()")[0]
                    classify_ = each.xpath("./div[@class='dd_lm']/a/text()")[0]
                    if classify_ in self.classify_tag:
                        item['classify'] = self.classify_map[classify_]
                        yield self.seeding(url, self.parse_article, meta=item)

    def parse_article(self, response):
        resp = response.etree_html
        item = response.meta
        content_ = get_content_from_html(resp, "//div[@class='left_zw']", 'a', 'strong', 'em')
        if content_ is None:
            return self.log.info('html未提取到内容，故放弃本次请求。')
        item['content_html'] = content_[0]
        item['content_text'] = content_[1]
        item['images'] = []
        images_ = content_[2]
        for img in images_:
            if not check_image(img):
                continue
            item['images'].append(img)
        item['article_type'] = 2 if item['images'] else 1

        item['source'] = '中国新闻网'
        item['web_source'] = '中国新闻网'
        item['cover'] = ''
        item['keywords'] = resp.xpath("//meta[@name='keywords']/@content")[0].split(',')
        datetime = ' '.join([resp.xpath("//input[@id='newsdate']/@value")[0],
                             resp.xpath("//input[@id='newstime']/@value")[0]])
        item['publish_timestr'] = datetime
        item['publish_timestamp'] = timestr_to_timestamp(datetime)
        self.save_to_mongo(item)


if __name__ == '__main__':
    spider = SpiderChinaNews()
    spider.run(start_seeds=True, clear_dups=True, clear_seeds=True)
