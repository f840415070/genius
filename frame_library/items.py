# -*- coding: utf-8 -*-
'''
@Date: 2020/1/13
@Author: fanyibin
@Description: None
'''
from frame_library.singleton import Singleton


class NewsItem(metaclass=Singleton):

    def __init__(self,
                 url, title, source, web_source, cover, content_text, content_html, images,
                 publish_timestr, publish_timestamp, keywords, article_type, classify):
        self.url = url,
        self.title = title,
        # 新闻来源
        self.source = source,
        # 网页来源
        self.web_source = web_source,
        # 封面图片 ->str
        self.cover = cover,
        # 文章文本 ->list
        self.content_text = content_text,
        # 文章html ->str
        self.content_html = content_html,
        # 图片列表 ->list
        self.images = images,
        # 时间格式化字符串 ->str
        self.publish_timestr = publish_timestr,
        # 毫秒级时间戳 ->int
        self.publish_timestamp = publish_timestamp,
        # ->list
        self.keywords = keywords,
        # ->int 纯文字：1；含图片；2
        self.article_type = article_type,
        # china='国内', world='国际', society='社会', law='法制', ent='娱乐', tech='科技',
        # life='生活', finance='财经', mil='军事', culture='文化',
        self.classify = classify,


if __name__ == '__main__':
    pass

