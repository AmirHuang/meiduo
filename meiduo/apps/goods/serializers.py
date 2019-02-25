# _*_ coding: utf-8 _*_
# @time     : 2018/12/10
# @Author   : Amir
# @Site     : 
# @File     : serializers.py
# @Software : PyCharm

from django_redis import get_redis_connection
from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers

from goods.models import SKU
from goods.search_indexes import SKUIndex


class CategoryListSerializers(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = "__all__"


class SKUSearchSeriazliers(HaystackSerializer):
    object = CategoryListSerializers()  # SKU商品数据对象序列化返回

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')


class SKUHistorySeriazliers(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('商品不存在')
        return attrs

    def create(self, validated_data):
        # 1、建立redis连接
        user = self.context['request'].user
        conn = get_redis_connection('history')
        # 2、判断sku——id是否保存过，保存过删除
        conn.lrem('history_%s' % user.id, 0, validated_data['sku_id'])
        # 3、写入sku——id
        conn.lpush('history_%s' % user.id, validated_data['sku_id'])
        # 4、控制保存数量
        conn.ltrim('history_%s' % user.id, 0, 4)
        # 返回结果
        return validated_data
