# _*_ coding: utf-8 _*_
# @time     : 2018/12/05
# @Author   : Amir
# @Site     : 
# @File     : models.py.py
# @Software : PyCharm

from django.db import models


class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        # 抽象模型类，迁移此文件不生成BaseModel表
        abstract = True

