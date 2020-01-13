# -*- coding: utf-8 -*-
'''
@Date: 2020/1/13
@Author: fanyibin
@Description: None
'''
from frame_library.singleton import Singleton


class NewsItem(Singleton):

    url = None,
    title = None,
    classify = None,
    source = None,
    web_source = None,
    cover = None,  # str
    content_text = None, # list
    content_html = None,
    images = None,  # list
    publish_timestr = None,
    publish_timestamp = None,  # int: ms level
    keywords = None,  # list
    article_type = None,  # int: 1->has no images; 2->has images

    news_classify = dict(
        china='国内',
        world='国际',
        society='社会',
        law='法制',
        ent='娱乐',
        tech='科技',
        life='生活',
        finance='财经',
        mil='军事',
        culture='文化',
    )