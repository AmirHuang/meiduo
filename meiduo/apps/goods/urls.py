# _*_ coding: utf-8 _*_
# @time     : 2018/12/10
# @Author   : Amir
# @Site     : 
# @File     : urls.py
# @Software : PyCharm

from django.urls import path, include, re_path
from goods import views

urlpatterns = [
    path("categories/<int:pk>/", views.CategoryView.as_view()),
    path(r"categories/<int:pk>/skus/", views.CategoryListView.as_view()),
    path(r'browse_histories/', views.SKUHistoryView.as_view()),
]

