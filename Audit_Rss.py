#-*- coding:utf-8 -*-
# rss订阅

import md5
import time
import logging
import pymysql
import urlparse
import requests
from module import feedparser

# 编码问题
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# https报错
requests.packages.urllib3.disable_warnings()


"""
    _      _      _
 __(.)< __(.)> __(.)=
 \___)  \___)  \___) 
"""
# Mysql配置
Mysql_config = {
    "host": "127.0.0.1",
    "user": "you username",
    "port": 3306,
    "password": "you password",
    "db": "auditrss",
    "charset": "utf8",
}

# 钉钉机器人token
ali_token = "我是马赛克"

# 关键词黑名单
black_list = ['zhaopin', u'招聘', u'诚聘', u'聘请', u'招人', u'招安全', u'聘安全', u'诚招', u'高薪']

class Mysql(object):

    def __init__(self):
        self.config = Mysql_config

    def connect(self, config):
        """
        连接mysql
        """
        conn = pymysql.connect(**config)
        return conn

    def query(self, sql, argv=None):
        """
        sql查询操作
        """
        result = False
        conn = self.connect(self.config)
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql, argv)
            result = cursor.fetchall()
        except Exception,e:
            conn.rollback()
            raise Exception(e)

        conn.close()
        return result

    def execute(self, sql, argv=None):
        """
        sql增删改操作
        """
        result = False
        conn = self.connect(self.config)
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            result = cursor.execute(sql, argv)
            conn.commit()
        except Exception, e:
            conn.rollback()
            raise Exception(e)

        conn.close()
        return result

class AliHook(object):

    def __init__(self):
        # 请求超时秒数
        self.timeout = 10
        # 发送请求次数
        self.num = 2
        self.sleep_time = 5

    def query(self, url, payload="", method="GET", header=""):
        """
        发送请求
        """
        nums = 0
        for num in range(0, self.num):
            nums += 1
            # 钉钉机器人一分钟只能发20条信息，所以sleep下
            time.sleep(self.sleep_time)
            try:
                if method == "GET":
                    response = requests.request(method, url, headers=header, verify=False, timeout=self.timeout)
                elif method == "POST":
                    response = requests.request(method, url, data=payload, headers=header, verify=False, timeout=self.timeout)
                break
            except Exception,e:
                logging.error("requests请求失败: {}, 正在进行第{}次尝试".format(str(e), nums))
                continue
        if nums == self.num:
            response = None
            logging.warn("[warning] url: {} 请求两次全部失败".format(data))
        return response

    def ali_hook(self, nickname, tag, title, urls):
        """
        阿里机器人
        """
        url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(ali_token)
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3071.115 Safari/537.36",
            "Host": urlparse.urlparse(url).netloc,
            "Content-Type": "application/json;charset=utf-8",
        }
        data = """
            {
                "msgtype": "markdown",
                "markdown": {
                        "title": "Security News",
                        "text": "> Author: %s<br>Tag: %s<br>Title: %s - [click read!](%s)"
                    }
            }
        """ % (str(nickname), str(tag), str(title), str(urls))
        response = self.query(url=url, payload=data, method="POST", header=header)
        print(response.content)

class Rss(object):

    def __init__(self):
        # 黑名单关键词
        self.black_list = black_list

    def _url_hash(self, url):
        """
        获取到url的hash
        """
        _u = urlparse.urlparse(url)
        # 防止协议更改
        _s = "{}{}{}{}{}".format(_u.netloc, _u.path, _u.params, _u.query, _u.fragment)
        new_md5 = (md5.new())
        new_md5.update(_s)
        return new_md5.hexdigest()

    def _checklist(self):
        """
        rss列表
        """
        sql = "SELECT * FROM checklist WHERE status=1"
        result = Mysql().query(sql)
        return result

    def _check_hash(self, id, hash):
        """
        对比hash
        """
        sql = "SELECT * FROM readlist WHERE checklist_id=%s AND hash=%s"
        argv = (id, hash)
        result = Mysql().query(sql, argv)
        return result

    def _data(self):
        """
        处理数据
        """
        rss_list = self._checklist()
        for item in rss_list:
            try:
                article_list = (feedparser.parse(item.get("url"))).entries
                _id = item.get("id")
                # 倒序输出
                for _c in reversed(article_list):
                    key = False
                    _url = _c.links[0].href
                    _title = _c.title
                    # 关键词黑名单
                    for _black in self.black_list:
                        if _black in _title:
                            key = True
                    if key: continue
                    _hash = self._url_hash(_url)
                    _status = self._check_hash(_id, _hash)
                    if not _status:
                        # 入库
                        _time = int(time.time())
                        sql = "INSERT INTO readlist(checklist_id, hash, add_time) VALUE('{}', '{}', '{}')".format(int(_id), _hash, _time)
                        Mysql().execute(sql)
                        print(_status, _title, _url, int(_id), _hash, _time)
                        # 钉钉机器人
                        AliHook().ali_hook(item.get("nickname"), item.get("tag"), _title, _url)
            except Exception,e:
                logging.warn(str(e))

    def main(self):
        while True:
            self._data()
            # 循环一次休眠2分钟
            time.sleep(120)

if __name__ == '__main__':
    obj = Rss()
    obj.main()
