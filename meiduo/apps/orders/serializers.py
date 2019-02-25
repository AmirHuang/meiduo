# _*_ coding: utf-8 _*_
# @time     : 2018/12/11
# @Author   : Amir
# @Site     : 
# @File     : serializers.py
# @Software : PyCharm

from decimal import Decimal
from datetime import datetime

from django_redis import get_redis_connection
from rest_framework import serializers
from django.db import transaction

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class SKUSerializers(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SKU
        fields = '__all__'


class OrderSerialzier(serializers.Serializer):
    skus = SKUSerializers(many=True)
    freight = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderSaveSerializes(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('address', 'pay_method', 'order_id')
        extra_kwargs = {
            'order_id': {
                'read_only': True
            },
            'address': {
                'write_only': True
            },
            'pay_method': {
                'write_only': True
            },
        }

    # @transaction.atomic()
    def create(self, validated_data):
        # 保存数据
        # 1. 获取用户
        user = self.context['request'].user
        # 2. 获取地址和支付方式
        address = validated_data['address']
        pay_method = validated_data['pay_method']
        # 3. 构建订单编号
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%06d' % user.id

        with transaction.atomic():
            # 建立保存点
            save_point = transaction.savepoint()
            try:
                # 4. 生成订单基本信息表
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0),
                    freight=Decimal(10),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']
                    else OrderInfo.ORDER_STATUS_ENUM['UNPAID'],
                )
                # 5. 查询选中状态的商品数据对象
                conn = get_redis_connection('carts')
                # 获取hash  sku_id  和 count
                sku_id_count = conn.hgetall('cart_%s' % user.id)  # {16:2}
                cart = {}
                for sku_id, count in sku_id_count.items():
                    cart[int(sku_id)] = int(count)
                # 获取set集合
                sku_ids = conn.smembers('cart_selected_%s' % user.id)
                # 根据集合中的sku_id获取商品对象
                # skus = SKU.objects.filter(id__in=sku_ids)

                for sku_id in sku_ids:
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        old_stock = sku.stock  # 原库存
                        old_salse = sku.sales  # 原销量
                        sku_count = cart[sku.id]

                        if sku_count > old_stock:
                            raise serializers.ValidationError('库存不足')

                        # 6. 更新sku中库存和销量
                        new_stock = old_stock - sku_count
                        new_salse = old_salse + sku_count
                        # sku.stock = new_stock
                        # sku.sales = new_salse
                        # sku.save()
                        ret = SKU.objects.filter(id=sku.id, stock=old_stock).update(stock=new_stock,
                                                                                    sales=new_salse)
                        if ret == 0:
                            continue
                        # 7、更新SPU中总销量
                        sku.goods.sales += sku_count
                        sku.goods.save()
                        # 8. 更新订单中的总价值 和 总量
                        order.total_amount += (sku.price * sku_count)
                        order.total_count += sku_count

                        # 9. 保存商品订单表
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price
                        )
                        break
                # 更新总价 加上运费
                order.total_amount += order.freight
                order.save()
            except:
                transaction.savepoint_rollback(save_point)
            else:
                transaction.savepoint_commit(save_point)
                # 10. 删除缓存中选中的商品id
                conn.hdel('cart_%s' % user.id, *sku_ids)
                conn.srem('cart_selected_%s' % user.id, *sku_ids)
                # 11. 结果返回
                return order
