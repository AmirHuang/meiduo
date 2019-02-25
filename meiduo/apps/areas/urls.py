# _*_ coding: utf-8 _*_
# @time     : 2018/12/07
# @Author   : Amir
# @Site     : 
# @File     : urls.py
# @Software : PyCharm

from django.urls import path, include, re_path
from .views import Area1View, AreaDumpView


urlpatterns = [
    path('areas/<int:pk>/', Area1View.as_view()),
    path('areadump/', AreaDumpView.as_view())
]