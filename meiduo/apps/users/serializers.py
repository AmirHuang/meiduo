# _*_ coding: utf-8 _*_
# @time     : 2018/12/05
# @Author   : Amir
# @Site     : 
# @File     : serializers.py
# @Software : PyCharm

import re
from django.conf import settings
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from users.models import User
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as TJSS
from celery_tasks.emil.tasks import send_email
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler


class UserSerialzier(serializers.ModelSerializer):
    # 显示指明模型类没有的字段
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'mobile', 'password', 'password2', 'sms_code', 'allow', 'id', 'token')
        # 额外参数添加
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 16,
                'min_length': 8,
                'style': {'input_type': 'password'},
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
            }
        }

    # 验证手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value

    # 验证协议
    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError('未同意协议')
        return value

    def validate(self, attrs):
        # 密码验证
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')

        # 短信验证
        # 1. 获取redis中真实的短信
        conn = get_redis_connection('smscodes')
        rel_sms_code = conn.get('smscode_%s' % attrs['mobile'])
        # 2. 判断短信是否验证过期
        if not rel_sms_code:
            raise serializers.ValidationError('短信验证码生效')
        # 3. 比对验证码
        if attrs['sms_code'] != rel_sms_code.decode():
            raise serializers.ValidationError('短信验证不一致')
        print(attrs)
        # 1. 删除无用的数据
        del attrs['password2']
        del attrs['sms_code']
        del attrs['allow']
        return attrs

    def create(self, validated_data):

        # 使用模型类保存
        user = User.objects.create_user(**validated_data)
        print('user:', user)

        # 生成加密的token
        # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    返回用户信息
    """

    class Meta:
        model = User
        exclude = ('password',)


class UserUpdateSerializer(serializers.ModelSerializer):
    """
      绑定邮箱账号并发送邮件
    """
    class Meta:
        model = User
        fields = ('email', )

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()
        tjss = TJSS(settings.SECRET_KEY, 300)
        token = tjss.dumps({'username': instance.username}).decode()
        verify_url = 'http://127.0.0.1:8000/emails/verification/?token=' + token
        subject = "美多商城用户邮箱验证"
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (validated_data['email'], verify_url, verify_url)
        # 异步发送邮件
        send_email(subject, validated_data['email'], html_message)

        # 往用户邮箱中发送验证信息
        return instance