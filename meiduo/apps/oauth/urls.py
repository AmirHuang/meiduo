# _*_ coding: utf-8 _*_
# @time     : 2018/12/06
# @Author   : Amir
# @Site     : 
# @File     : urls.py
# @Software : PyCharm

from django.urls import path, include, re_path
from .views import OauthQQloginView, OauthView


urlpatterns = [
    path('qq/authorization/', OauthQQloginView.as_view()),
    path('qq/user/', OauthView.as_view())
]
