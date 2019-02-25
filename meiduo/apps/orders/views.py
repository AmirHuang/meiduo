from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django_redis import get_redis_connection
# Create your views here.
from goods.models import SKU
from decimal import Decimal

from orders.serializers import OrderSerialzier, OrderSaveSerializes


class OrderShowView(APIView):
    """
        获取订单商品信息
    """
    def get(self, request):
        # 1. 建立redis链接
        conn = get_redis_connection('carts')
        # 2. 获取用户
        user = request.user
        # 3. 获取hash sku_id 和 count
        sku_id_count = conn.hgetall('cart_%s' % user.id)  # {16:2}
        cart = {}
        for sku_id, count in sku_id_count.items():
            cart[int(sku_id)] = int(count)
        # 4. 获取set集合
        sku_ids = conn.smembers('cart_selected_%s' % user.id)
        # 5.根据集合中的sku_id 获取商品对象
        skus = SKU.objects.filter(id__in=sku_ids)
        # 6. 给商品数据对象添加count
        for sku in skus:
            sku.count = cart[sku.id]
        # 7. 指定运费
        freight = Decimal(10.00)
        # 8. 序列化返回
        ser = OrderSerialzier({'freight': freight, 'skus': skus})

        return Response(ser.data)


class OrderSaveView(CreateAPIView):
    """
        保存订单
    """
    serializer_class = OrderSaveSerializes