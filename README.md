## genius 基于Python的爬虫框架

**0. genius**<br>

- 本地***快速***爬取
- ***一句代码***轻松部署到***线上***
- 线上***定时***爬虫，配置周期***自动启动***
- ***去重***机制
- ***日志***功能
- ***易操作，支持扩展内容***
- 请求超时***自动重连***
- 发生异常***不会终止***爬虫

**1. 使用框架**<br>

- 请直接clone到环境
```
git clone https://github.com/f840415070/genius.git
```

**2. 安装工具及第三方库**<br>

- python3
- redis
- mongodb
- 第三方库详见requirements.txt <br>
安装命令`pip install -r requirements.txt`

**3. 配置文件** <br>
文件地址：`genius/config/`

- settings.ini
    - `DEBUG`，默认True本地运行，服务器上框架请修改为`DEBUG=False`
    - `LOG_PATH`，此为log文件存放地址，请填写一个绝对路径，推荐在项目内log文件夹下
    - `LOG_ENABLED` 禁用log功能请改为False，建议开启
- debug_config.ini
    - 本地运行框架必填连接配置，默认local配置，可远程连接
    - redis, mongo 至少配置到`HOST`, `PORT`, `DB`
    - 没有身份认证可不填`USERNAME`, `PASSWORD`
- server_config.ini
    - 线上运行框架需填写连接配置，可远程连接
    - redis, mongo 至少配置到`HOST`, `PORT`, `DB`
    - 没有身份认证可不填`USERNAME`, `PASSWORD`
    
**4. DEMO** <br>

爬虫请存放在`genius/spiders/` <br>

- 编写代码

spider_demo.py

```python
from core.genius import Genius # 引入Genius类


class SpiderDemo(Genius): # 继承Genius类
    name = 'demo' # 爬虫需要命名
    url = 'https://www.demo.com' # url
    
    def start_requests(self): # 初始请求，生成初始访问的种子请求
        yield self.seeding(self.url, 'parse') # 生成访问url的请求种子， 指定parse函数来解析响应结果
        # seeding必填参数url, parse_func;
        # 可选参数等同于 requests请求参数，method=None, data=None, params=None, cookies=None, headers=None, meta=None, encoding=None, filter_item=False, **kwargs
        # headers不指定，user-agent将会从genius/downloader/user_agent_pool 随机取出
        # filter_item，去重参数，值为bool类型，默认False，开启后将自动根据访问的url去重
        # encoding 指定响应体编码，默认utf-8
        # meta传递一个值到解析函数里，通过response.meta使用
            
    def parse(self, response): # 解析函数有且只有一个参数，通过这个参数来调用响应
        '''
        response.response 等同于 requests.get() 返回下载的响应
        '''
        text = response.text # 等同于 requests.get().text
        content = response.content # 等同于 requests.get().content
        res_json = response.json # 等同于 requests.get().json()
        html = response.etree_html # response.etree_html 返回一个etree.HTML对象，可以使用xpath解析, 也可以自行封装其他解析库，bs4，pyquery等...
        
        urls = html.xpath("...")
        for url in urls:
            if self.filter_item(url):  # filter_item 将会根据参数去重，下一次访问该url将会被去重过滤掉
                data = {'number': 123}
                yield self.seeding(url, 'parse2', meta=data) # 生成访问所有urls的请求种子解析函数为parse2，向parse2函数传递一个字典
        
    def parse2(self, response):
        item = response.meta # 上一层传过来的meta值, {'number': 123}
        item['text'] = response.text
        self.save_to_mongo(item) # 将爬到的数据保存到mongodb
        
        
if __name__ == '__main__':
    # 本地运行需要实例对象运行
    demo = SpiderDemo()
    demo.run(start_seeds=True) # 初次运行需要生成初始种子，即运行start_request
                               # 可选参数 clear_seeds=False 清除库存的种子, clear_dups=False 清除所有去重的记录

```

- 服务器上运行，仅限Linux系统，环境为python3<br>
    - a.编写代码
    - b.配置文件
        - settings修改DEBUG=True
        - server_config.ini需配置好redis、mongodb连接属性
        - spider_config.ini配置定时爬虫，定时使用的是Apscheduler（设置trigger可定时、间隔、指定时间运行），详细使用自行百度学习<br>`demo = {'trigger': 'cron', 'hour': 8, 'file': 'spider_demo', 'class': 'SpiderDemo'}`
        <br>'trigger': 'cron' - 定时运行，'hour': 8 - 每天8点运行，'file' - 爬虫文件名，'class' - 爬虫类名
    - c.运行爬虫<br>
    在项目根目录genius/下执行命令`python3 manager.py -命令参数 爬虫名`<br>
    生成初始种子：``python3 manager.py -s demo``<br>
    运行爬虫：``python3 manager.py -r demo``<br>
    其他参数：-k 停止运行爬虫， -c 清除该爬虫所有请求种子 -cd 清除该爬虫所有去重记录 -rs 重启爬虫 -v 查看爬虫是否在后台运行<br>
    `python3 all.py --命令参数 all` 可操作所有爬虫，命令请查看文件 all.py，这里不再赘述

**5. 流程实现**<br>

- 通过运行初始请求函数`start requests`将种子队列保存到redis `list`结构里
- 每次取出最新一条请求种子（种子队列先进后出），请求url下载并获取响应，执行解析函数，或又生成种子
- 直到redis爬虫请求队列里没有种子了，爬虫结束（线上爬虫会等待框架根据定时配置定时生成种子）
- 线上运行爬虫只需第一次生成初始种子，后面定时器会按照配置周期自动运行`start requests`生成种子

**6. 其他**<br>

- 以上！