# -*- coding: utf-8 -*-
'''
@Date: 2019/12/30
@Author: fanyibin
@Description: None
'''
from frame_library.singleton import Singleton
from frame_library.logger import get_log_config
from frame_library.duplicater import Duplicater
from seed.seed import Seed
from frame_library.common_library import current_timestamp, current_timestr


class SpiderMiddleware(metaclass=Singleton):
    def __init__(self):
        self.log = get_log_config()
        self.dup = Duplicater()
        self.dupname_suffix = 'dup'

    def check_seed(self, seed):
        if isinstance(seed, Seed):
            if not all([seed.url, seed.parse_func]):
                self.log.warning('seed实例url或parse_func参数为空，无法生成种子。')
                return None
            return seed
        else:
            self.log.warning('seed不是Seed类实例，无法生成种子。')
            return None

    def handle_seed(self, seed, name):
        this_seed = self.check_seed(seed)
        if this_seed:
            if this_seed.filter_item:
                name_dup = ':'.join((name.split(':')[0], self.dupname_suffix))
                result = self.dup.duplicate(name_dup, seed.url)
                if not result:
                    return None
            return this_seed

    def check_item(self, item):
        if isinstance(item, dict):
            return item
        else:
            self.log.warning('save失败！结果数据必须为<dict>类型，实际为{}；将不会保存至数据库。'.format(type(item)))
            return None

    def handle_item(self, item, spider_name):
        this_item = self.check_item(item)
        if this_item is None:
            return None
        this_item.update({
            'update_timestr': current_timestr(),
            'update_timestamp': current_timestamp(),
            'spider_name': spider_name,
        })
        return this_item