# _*_ coding: utf-8 _*_
# @time     : 2018/12/11
# @Author   : Amir
# @Site     : 
# @File     : urls.py
# @Software : PyCharm


from django.urls import path, include, re_path
from . import views


urlpatterns = [
    path(r'orders/settlement/', views.OrderShowView.as_view()),
    path(r'orders/', views.OrderSaveView.as_view()),
]
