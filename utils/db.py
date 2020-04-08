# -*- coding:utf-8 -*-
# 数据表

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CheckList(Base):
    __tablename__ = 'checklist'

    id = Column(Integer, primary_key=True)
    nickname = Column(String(255))
    tag = Column(String(255))
    url = Column(String(255))
    status = Column(Integer)


class ReadList(Base):
    __tablename__ = 'readlist'

    id = Column(Integer, primary_key=True)
    checklist_id = Column(Integer)
    hash = Column(String(255))
    add_time = Column(Integer)
