# AuditRss
![][Python 2.7.13] ![][Mysql 5.6+]
> AuditRss用于监控大佬博客的Rss，然后推送到钉钉。

依赖
----
```
pip install -r requirements.txt
```

配置
----
#### ./config/config.py
```
# Mysql配置
mysql_host = "127.0.0.1"
mysql_port = "3306"
mysql_user = "root"
mysql_pass = "root"
mysql_database = "auditrss"

# 钉钉机器人token
ding_robot_token = "钉钉申请的机器人token"
```
### 【注意】然后Mysql source该项目下面的auditrss.sql文件！！

运行
----
```
python Audit_Rss.py
```

效果
----
![效果][hhh]

参考
----
[钉钉机器人文档][alihook]

[Python 2.7.13]: https://img.shields.io/badge/python-2.7.13-brightgreen.svg
[Mysql 5.6+]: https://img.shields.io/badge/Mysql-5.6+-red.svg
[hhh]: https://image.ibb.co/g7JDLx/111111.jpg
[alihook]: https://open-doc.dingtalk.com/docs/doc.htm?treeId=257&articleId=105733&docType=1
