# _*_ coding: utf-8 _*_
# @time     : 2018/12/10
# @Author   : Amir
# @Site     : 
# @File     : urls.py
# @Software : PyCharm


from django.urls import path, include, re_path
from django.conf.urls import url
from django.contrib import admin
from . import views


urlpatterns = [
    path(r'cart/', views.CartsView.as_view()),
    path(r'cart/selection/', views.CartsSelectedView.as_view()),
]