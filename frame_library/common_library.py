# -*- coding: utf-8 -*-
'''
@Date: 2019/12/27
@Author: fanyibin
@Description: None
'''
import time
import re
from w3lib.html import remove_tags
from lxml import etree

counting_map = {
    'd': '%Y-%m-%d',
    'M': '%Y-%m-%d %H:%M',
    'S': '%Y-%m-%d %H:%M:%S',
}


def timestr_to_timestamp(time_str):
    # 时间字符串转化为毫秒级时间戳
    counting = 'S'
    if not re.match('^\d+-\d+-\d+ \d+:\d+:\d+$', time_str):
        if re.match('^\d+-\d+-\d+$', time_str):
            counting = 'd'
        elif re.match('^\d+-\d+-\d+ \d+:\d+$', time_str):
            counting = 'M'

    time_array = time.strptime(time_str, counting_map[counting])
    time_stamp = int(time.mktime(time_array) * 1000)
    return time_stamp


def timestamp_to_timestr(timestamp, counting='S'):
    # 时间戳转化为时间字符串
    timestr = time.strftime(counting_map[counting], time.localtime(timestamp))
    return timestr


def current_timestr():
    # 返回当前日期字符串
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def current_timestamp():
    # 返回当前时间戳，毫秒级
    return int(time.time() * 1000)


def get_content_from_html(etree_obj, xpath_exp, *args):
    '''
    提取内容
    :param etree_obj: etree.HTML对象
    :param xpath_exp: xpath表达式
    :param args: 任意标签字符串，将会被移除
    :return:
    '''
    ret_ = etree_obj.xpath(xpath_exp)
    if not ret_:
        return None

    content_html = etree.tostring(ret_[0], encoding='utf-8').decode()
    html_ = etree.HTML(remove_tags(content_html, which_ones=args))
    raw_text = html_.xpath("//p/text()")
    if not raw_text:
        return None
    handle_raw_text = map(lambda s: s.replace(u'\u3000', ' ').strip(), raw_text)
    text = []
    list(map(lambda s: text.append(s) if s else None, handle_raw_text))
    images = re.findall(r'src="(.*?)"', content_html)
    return content_html, text, images


def check_image(img):
    if any([i in img for i in ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')]):
        return True
    return False


if __name__ == '__main__':
    print(timestamp_to_timestr(1571358312683))
