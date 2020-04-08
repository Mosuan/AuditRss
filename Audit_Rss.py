# -*- coding: utf-8 -*-
# rss订阅

import time
import hashlib
import logging
import urlparse
import requests

from utils.db import *
from config.config import *
from utils import feedparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


import sys
reload(sys)
sys.setdefaultencoding("utf8")

# https报错
requests.packages.urllib3.disable_warnings()

# 创建数据库连接
engine = create_engine(mysql_client)

Session = sessionmaker(bind=engine)
session = Session()


class AliHook(object):

    def __init__(self):
        # 请求超时秒数
        self.timeout = 10
        # 发送请求次数
        self.num = 2
        self.sleep_time = 5

    def query(self, url, payload="", method="GET", header=None):
        """
        发送请求
        """
        nums = 0
        response = None
        for num in range(0, self.num):
            nums += 1
            try:
                if method == "GET":
                    response = requests.request(method, url, headers=header, verify=False, timeout=self.timeout)
                elif method == "POST":
                    response = requests.request(method, url, data=payload, headers=header, verify=False,
                                                timeout=self.timeout)
                break
            except Exception as e:
                logging.error("requests请求失败: {}, 正在进行第{}次尝试".format(str(e), nums))
                continue
        if nums == self.num:
            logging.warn("[warning] url: {} 请求两次全部失败".format(url))
        # 钉钉机器人一分钟只能发20条信息，所以sleep下
        time.sleep(self.sleep_time)
        return response

    def ali_hook(self, nickname, tag, title, urls):
        """
        阿里机器人
        """
        url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(ding_robot_token)
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) Chrome/58.0.3071.115 Safari/537.36",
            "Host": "oapi.dingtalk.com",
            "Content-Type": "application/json;charset=utf-8",
        }
        data = """
            {
                "msgtype": "markdown",
                "markdown": {
                        "title": "Security News",
                        "text": "> Author: %s\n\n> Tag: %s\n\n> Title: %s - [click read!](%s)"
                    }
            }
        """ % (str(nickname), str(tag), str(title), str(urls))
        response = self.query(url=url, payload=data, method="POST", header=header)
        print(response.content)


class Rss(object):

    def __init__(self):
        # 黑名单关键词
        self.black_list = black_list

    @staticmethod
    def _url_hash(url):
        """
        获取到url的hash
        """
        _u = urlparse.urlparse(url)
        # 防止协议更改
        _s = "{}{}{}{}{}".format(_u.netloc, _u.path, _u.params, _u.query, _u.fragment)
        new_md5 = hashlib.md5()
        new_md5.update(_s)
        return new_md5.hexdigest()

    @staticmethod
    def _check_hash(ids, url_hash):
        """
        对比hash
        """
        read_result = session.query(ReadList).filter(ReadList.checklist_id == ids, ReadList.hash == url_hash).first()
        return read_result

    def main(self):
        """
        处理数据
        """
        rss_list = session.query(CheckList).filter(CheckList.status == 1).all()
        for item in rss_list:
            try:
                article_list = (feedparser.parse(item.url)).entries
                # 倒序输出
                for _c in reversed(article_list):
                    black_list_key = False
                    # 关键词黑名单
                    for _black in self.black_list:
                        if _black in _c.title:
                            black_list_key = True
                    if black_list_key:
                        continue
                    _hash = self._url_hash(_c.link)
                    _status = self._check_hash(item.id, _hash)
                    if not _status:
                        # 入库
                        _time = int(time.time())
                        read_info = ReadList(checklist_id=int(item.id), hash=_hash, add_time=_time)
                        session.add(read_info)
                        session.commit()
                        # 钉钉机器人
                        AliHook().ali_hook(item.nickname, item.tag, _c.title, _c.link)
            except Exception as e:
                logging.warn("_data error: {}".format(str(e)))

if __name__ == '__main__':
    while True:
        Rss().main()
        time.sleep(120)
