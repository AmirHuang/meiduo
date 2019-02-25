# _*_ coding: utf-8 _*_
# @time     : 2018/12/04
# @Author   : Amir
# @Site     : 
# @File     : serializers.py
# @Software : PyCharm

import re
from rest_framework import serializers
from areas.models import Area
from users.models import Address


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = '__all__'


class AddressesSerializer(serializers.ModelSerializer):
    # 显示指定字段
    city_id = serializers.IntegerField(min_value=1, write_only=True)
    # city_id = serializers.SlugRelatedField(slug_field='pk', queryset=Area.objects.all())
    district_id = serializers.IntegerField(min_value=1, write_only=True)
    province_id = serializers.IntegerField(min_value=1, write_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        exclude = ('user', )

    # 验证手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value

    # 保存新增地址
    def create(self, validated_data):

        user = self.context['request'].user
        # 需要在验证后数据中添加user
        validated_data['user'] = user
        # 使用父类保存方法
        address = super().create(validated_data)
        return address
