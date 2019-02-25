# _*_ coding: utf-8 _*_
# @time     : 2018/12/06
# @Author   : Amir
# @Site     : 
# @File     : serializers.py.py
# @Software : PyCharm

import re

from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from oauth.models import OAuthUser
from users.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as  TJSS


class OauthSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    access_token = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    mobile = serializers.CharField(max_length=11)

    class Meta:
        model = User
        fields = ('password', 'mobile', 'username', 'sms_code', 'token', 'access_token', 'user_id')

        extra_kwargs = {
            'username': {
                'read_only': True
            },
            'password': {
                'write_only': True
            }
        }

    # 验证手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value

    def validate(self, attrs):
        # 验证access_token
        # 解密
        tjss = TJSS(settings.SECRET_KEY, 300)
        try:
            data = tjss.loads(attrs['access_token'])
        except:
            raise serializers.ValidationError('access_token无效')

        # 获取openid
        openid = data.get('openid')
        # attrs添加属性
        attrs['openid'] = openid
        # 验证短信验证码
        # 1. 获取redis中真实短信
        conn = get_redis_connection('smscodes')
        rel_sms_code = conn.get('smscode_%s' % attrs['mobile'])
        # 2. 判断redis中短信是否有效
        if not rel_sms_code:
            raise serializers.ValidationError('短信验证码失效')
        # 3. 比对用户输入的短信和redis中真实短信
        if attrs['sms_code'] != rel_sms_code.decode():
            raise serializers.ValidationError('短信验证不一致')

        # 判断手机号是否注册过
        try:
            user = User.objects.get(mobile=attrs['mobile'])
        except:
            # 未注册 就注册为新用户
            return attrs
        else:
            # 注册过，就检查用户进行绑定
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码错误')
            attrs['user'] = user
            print(attrs)
            return attrs

    def create(self, validated_data):
        # 判断用户
        user = validated_data.get('user', None)
        if user is None:
            # 创建用户
            user = User.objects.create_user(username=validated_data['mobile'],
                                            password=validated_data['password'],
                                            mobile=validated_data['mobile'])
        # 绑定操作
        OAuthUser.objects.create(user=user, openid=validated_data['openid'])
        # 生成加密后的token值
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # user 添加属性token 和 user_id
        user.token = token
        user.user_id = user.id
        return user


