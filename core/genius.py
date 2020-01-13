# -*- coding: utf-8 -*-
'''
@Date: 2019/12/14
@Author: fanyibin
@Description: None
'''
from frame_library.logger import get_log_config
from seed.seed import Seed
from seed.seed_manager import SeedManager
from downloader.requester import Requester
from collections.abc import Iterable
from frame_library.duplicater import Duplicater
from pipeline.mongo_pipe import MongoPipe
from config.config_parser import get_config
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import traceback


class Genius(object):
    """所有爬虫需继承此类"""
    name = ''  # 子类爬虫重写该属性，为爬虫命名，规定为小写英文字符

    def __init__(self):
        if not self.name.strip():
            raise Exception('子类爬虫必须重写 name ，请为爬虫命名。')
        self.name = self.name.lower()
        self.__name_seed = ':'.join([self.name, 'seed'])
        self.__name_dup = ':'.join([self.name, 'dup'])

        self.log = get_log_config(self.name)
        self.__req = Requester()
        self.__manager = SeedManager()
        self.__dup = Duplicater()
        self.__mongopipe = MongoPipe()
        self.__sched = BlockingScheduler()

        self.__settings = get_config('settings.ini')
        self.__debug = self.__settings.getboolean('MODE', 'DEBUG')
        self.__sleep_interval = self.__settings.getint('FRAME_SETTINGS', 'SLEEP_INTERVAL')

        self.__req_count = 0
        self.__resp_count = 0
        self.__save_count = 0
        self.__err_count = 0

    @property
    def __spider_conf(self):
        _spider_config = get_config('spider_config.ini').get('SPIDERS', self.name)
        spider_conf = eval(_spider_config)
        spider_conf.pop('file')
        spider_conf.pop('class')
        return spider_conf

    def seeding(self, url, parse_func,
                method=None, data=None, params=None, cookies=None, headers=None, meta=None, encoding=None,
                filter_item=False, **kwargs):
        """yield此方法生成种子"""
        allkwargs = dict(method=method, data=data, params=params, cookies=cookies,
                         headers=headers, meta=meta, encoding=encoding, filter_item=filter_item)
        allkwargs.update(kwargs)
        return Seed(url, parse_func, **allkwargs)

    def save_to_mongo(self, item):
        """提供接口存储数据至mongodb"""
        ret = self.__mongopipe.save_item(self.name, item)
        if ret:
            self.__save_count += 1
        else:
            self.__err_count += 1
        return ret

    def filter_item(self, item):
        """在解析函数里使用，过滤指定项，达到去重的目的"""
        result = self.__dup.duplicate(self.__name_dup, item)
        return result

    def clear_debug_seeds(self):
        """清空种子队列"""
        self.__manager.clear_seeds(self.__name_seed)

    def clear_debug_dups(self):
        """清空去重记录"""
        self.__manager.clear_dups(self.__name_dup)

    def __run_once(self):
        """
        运行逻辑：
            取出一条种子 -> 请求种子，获取响应 -> 执行解析函数 -> 解析函数不生产种子，redis种子队列无种子，爬虫结束
                                                           -> 解析函数生产种子，循环此逻辑，直到当前爬虫再无种子
        :return:
        """
        seed = self.__manager.pop_seed(self.__name_seed)
        resp = self.__get_response(seed)
        if resp is None:
            return
        self.__resp_count += 1
        setattr(seed, 'response', resp)
        try:
            parse_func_result = getattr(self, seed.parse_func)(seed)
        except:
            self.log.warning('解析出错！异常追踪如下：')
            self.log.error(traceback.format_exc())
            self.__err_count += 1
            return

        if isinstance(parse_func_result, Iterable):
            self.__push_seeds(parse_func_result)

    def __get_response(self, seed):
        """获取响应"""
        self.__req_count += 1
        response = self.__req.get_response(seed)
        return response

    def __reinit_count(self):
        self.__req_count = 0
        self.__resp_count = 0
        self.__save_count = 0
        self.__err_count = 0

    def start_requests(self):
        """爬虫的入口，重写方法，使用yield生成初始种子"""
        pass

    def make_start_seeds(self):
        """生成初始种子"""
        start_req_result = self.start_requests()
        if isinstance(start_req_result, Iterable):
            self.__push_seeds(start_req_result)
        else:
            self.log.error('初始请求有误：start_requests不可迭代，没有种子生成！请检查代码。是否忘记了关键词【yield】？')

    def __push_seeds(self, iter_func_result):
        for seed in iter_func_result:
            self.__manager.push_seed(self.__name_seed, seed)

    def get_seed_status(self):
        self.log.info('<{}> 库存种子数量：{}。'.format(self.name, self.__seed_count))

    @property
    def __seed_count(self):
        return self.__manager.get_seed_count(self.__name_seed)

    def __run_pre(self, start_seeds, clear_seeds, clear_dups):
        self.log.info('爬虫启动，进行前置处理。')
        self.get_seed_status()
        if clear_seeds:
            self.clear_debug_seeds()
        if clear_dups:
            self.clear_debug_dups()
        if start_seeds:
            self.make_start_seeds()

    def __run_end(self):
        self.get_seed_status()
        self.log.info('已爬取完所有种子，爬虫结束。')
        text = 'Request Count: %d\nResponse Count: %d\nSave Items: %d\nError Count: %d\n' % (
            self.__req_count, self.__resp_count, self.__save_count, self.__err_count
        )
        self.log.info('本次爬虫统计如下：\n{}'.format(text))
        self.__reinit_count()

    def run(self, start_seeds=False, clear_seeds=False, clear_dups=False):
        """
        :param start_seeds: 生成初始种子
        :param clear_seeds: 清空该爬虫所有库存种子
        :param clear_dups: 清空该爬虫所有去重记录
        :return:
        """
        self.__run_pre(start_seeds, clear_seeds, clear_dups)
        while self.__seed_count:
            self.__run_once()
        self.__run_end()

    def __add_sched_job(self):
        """生成定时任务"""
        self.__sched.add_job(self.make_start_seeds, **self.__spider_conf)
        self.__sched.add_job(self.__run_server, trigger='interval', seconds=self.__sleep_interval,
                             next_run_time=datetime.now())

    def __run_server(self):
        if self.__seed_count:
            while self.__seed_count:
                self.__run_once()
            self.__run_end()

        self.log.info('库存种子数量为0，爬虫将休眠{}s，休眠结束后将重新扫描种子。'.format(self.__sleep_interval))
        self.log.info('爬虫休眠中...')

    def run_server(self):
        if self.__debug:
            text = '现在是debug模式，运行线下爬虫请使用run方法。若要使用run_server方法，请在settings.ini修改DEBUG=False。'
            return self.log.error(text)

        self.__add_sched_job()
        self.__sched.start()
