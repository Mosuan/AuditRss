# -*- coding: utf-8 -*-
# 配置文件 key=localhost为本地测试环境， prd为线上环境

key = "localhost"

# 标题关键词黑名单
black_list = ['zhaopin', u'招聘', u'诚聘', u'聘请', u'招人', u'招安全', u'聘安全', u'诚招', u'高薪']

if key == "localhost":
    # Mysql 配置
    mysql_host = "127.0.0.1"
    mysql_port = "3306"
    mysql_user = "root"
    mysql_pass = "root"
    mysql_database = "auditrss"

    # 钉钉 Token
    ding_rebot_token = "42324e163c710abb0a4537701cda0ce043a00d5dec34d2d07c2bd8a2de57d59c"

else:
    # Mysql 配置
    mysql_host = "127.0.0.1"
    mysql_port = "3306"
    mysql_user = "root"
    mysql_pass = "root"
    mysql_database = "auditrss"

    # 钉钉 Token
    ding_rebot_token = "42324e163c710abb0a4537701cda0ce043a00d5dec34d2d07c2bd8a2de57d59c"


mysql_client = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(mysql_user, mysql_pass, mysql_host, int(mysql_port),
                                                       mysql_database)
