# _*_ coding: utf-8 _*_
# @time     : 2018/12/05
# @Author   : Amir
# @Site     : 
# @File     : urls.py
# @Software : PyCharm


from django.conf.urls import url
from django.urls import path, include, re_path

from .views import SmsCode, UserNameView, MobileView, UserUpdateView, EmailVerifyView
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('sms_code/<str:mobile>/', SmsCode.as_view()),
    path('username/<str:username>/count/', UserNameView.as_view()),
    path('mobile/<str:mobile>/count/', MobileView.as_view()),
    path('email/', UserUpdateView.as_view()),
    path("emails/verification/", EmailVerifyView.as_view()),
]