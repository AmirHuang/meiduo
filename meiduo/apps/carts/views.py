from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
# Create your views here.
from carts.serializers import CartsSerialziers, CartListSeriazlier, CartsDeleteSerialziers, CartsSelectedSerialziers
import pickle, base64

from goods.models import SKU


class CartsView(APIView):
    """
        购物车数据的增删改查
    """

    def perform_authentication(self, request):
        # 不再调用post方法之前进行验证
        # request.user
        pass

    def post(self, request):
        # 1. 获取数据
        data = request.data
        # 2. 验证数据
        ser = CartsSerialziers(data=data)
        ser.is_valid()
        print('ser.errors:', ser.errors)
        # 获取验证后的数据
        sku_id = ser.validated_data['sku_id']
        count = ser.validated_data['count']
        selected = ser.validated_data['selected']

        # 3. 判断用户登陆状态
        try:
            user = request.user
        except:
            user = None
        if user is not None:
            # 4. 已登陆 保存redis
            # 1. 建立链接
            conn = get_redis_connection('carts')
            # 2. 写入hash sku_id 和 count
            conn.hincrby('cart_%s' % user.id, sku_id, count)
            # 3. 写入set
            if selected:
                conn.sadd('cart_selected_%s' % user.id, sku_id)
                # 4. 结果返回
                return Response({'message': 'ok'})
        else:
            # 5. 未登陆 保存cookie
            response = Response({'message': 'ok'})
            # 1. 先获取cookie, 判断原来是否写入过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            if cart_cookie:
                # 2. 写入过.解密.cart = {10: {‘count’:2, selected: True}
                cart = pickle.loads(base64.b64decode(cart_cookie))
            else:
                # 3、未写入过cart = {}
                cart = {}
            # 4. 判断sku_id 是否存在 累加
            sku = cart.get(sku_id)
            if sku:
                count += int(sku['count'])
            # 5. 写入新数据
            cart[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 6. 加密操作
            cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            # 7. 写入cookie
            response.set_cookie('cart_cookie', cart_cookie, max_age=60*60*24)
            # 8. 结果返回
            return response

    def get(self, request):
        # 1. 判断用户登陆状态
        try:
            user = request.user
        except:
            user = None
        if user is not None:
            # 2. 已登陆 保存redis
            # 1. 建立链接
            conn = get_redis_connection('carts')
            # 2. 获取hash sku-id 和 count
            sku_id_count = conn.hgetall('cart_%s' % user.id)
            # 3. 获取set
            selecteds = conn.smembers('cart_selected_%s' % user.id)
            # 4. 构建字典数据
            cart = {}
            for sku_id, count in sku_id_count.items():
                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in selecteds
                }
        else:
            # 3. 未登陆，保存cookie
            # 1、先获取cookie，判断原来是否写入过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            if cart_cookie:
                # 2、写入过。解密.cart = {10: {‘count’:2, selected: True}
                cart = pickle.loads(base64.b64decode(cart_cookie))
            else:
                # 3、未写入过cart = {}
                cart = {}
        # 4、获取字典中的sku_id
        sku_ids = cart.keys()
        # 5. 根据sku—id 查询商品数据对象
        skus = SKU.objects.filter(id__in=sku_ids)

        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        # 6. 序列化返回数据对象
        ser = CartListSeriazlier(skus, many=True)

        return Response(ser.data)

    def put(self, request):
        # 1. 获取数据
        data = request.data
        # 2. 验证数据
        ser = CartsSerialziers(data=data)
        ser.is_valid()
        print(ser.errors)
        # 获取验证后数据
        sku_id = ser.validated_data['sku_id']
        count = ser.validated_data['count']
        selected = ser.validated_data['selected']
        # 3. 判断登陆状态
        try:
            user = request.user
        except:
            user = None
        if user is not None:
            # 4. 已登陆，保存redis
            # 1. 建立链接
            conn = get_redis_connection('carts')
            # 2. 更新hash sku-id 和 cout
            conn.hset('cart_%s' % user.id, sku_id, count)
            # 3. 更新set
            if selected:
                conn.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                conn.srem('cart_selected_%s' % user.id, sku_id)
            # 4. 结果返回
            return Response({'count': count})
        else:
            # 5. 未登陆 保存cookie
            response = Response({'count': count})
            # 1. 先获取cookie 判断原来是否写入过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            if cart_cookie:
                # 2、写入过。解密.cart = {10: {‘count’:2, selected: True}
                cart = pickle.loads(base64.b64decode(cart_cookie))
            else:
                # 3、未写入过cart = {}
                cart = {}
            # 4. 写入新数据
            cart[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 5. 加密操作
            cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            # 6. 写入cookie
            response.set_cookie('cart_cookie', cart_cookie, max_age=60*60*24)
            # 9. 结果返回
            return response

    def delete(self, request):
        # 1. 获取数据
        data = request.data
        # 2. 验证数据
        ser = CartsDeleteSerialziers(data=data)
        ser.is_valid()
        print(ser.errors)
        # 获取验证后数据
        sku_id = ser.validated_data['sku_id']
        # 3. 判断用户登陆状态
        try:
            user = request.user
        except:
            user = None
        if user is not None:
            # 4. 已登陆 删除redis
            # 1. 建立链接
            conn = get_redis_connection('carts')
            # 2. s删除hash sku—id 和 count
            conn.hdel('cart_%s' % user.id, sku_id)
            # 3. 删除set
            conn.srem('cart_selected_%s' % user.id, sku_id)
            # 4. 结果返回
            return Response({'message': 'ok'})
        else:
            # 5. 未登录 保存cookie
            response = Response({'message': 'ok'})
            # 1.先获取cookie 判断是否写入过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            if cart_cookie:
                # 2. 写入过 解密.cart = {10: {‘count’:2, selected: True}
                cart = pickle.loads(base64.b64decode(cart_cookie))
                # 3. 删除数据
                if sku_id in cart.keys():
                    del cart[sku_id]
                # 4. 加密操作
                cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
                # 5. 写入cookie
                response.set_cookie('cart_cookie', cart_cookie, max_age=60*60*24)
            return response


class CartsSelectedView(APIView):
    def perform_authentication(self, request):
        # 不再调用put方法之前进行验证
        # request.user
        pass

    def put(self, request):
        # 1. 获取数据
        data = request.data
        # 2. 验证数据
        ser = CartsSelectedSerialziers(data=data)
        ser.is_valid()
        print(ser.errors)
        # 获取验证后数据
        selected = ser.validated_data['selected']
        # 3. 判断用户登陆状态
        try:
            user = request.user
        except:
            user = None
        if user is not None:
            # 4. 已登陆 保存redis
            # 1. 建立链接
            conn = get_redis_connection('carts')
            # 2. 获取hash sku-id 和 count
            sku_id_count = conn.hgetall('cart_%s' % user.id)  # {1:2}
            sku_ids = sku_id_count.keys()  # [1,2,3]
            # 3. 更新set
            if selected:
                conn.sadd('cart_selected_%s' % user.id, *sku_ids)
            else:
                conn.srem('cart_selected_%s' % user.id, *sku_ids)
            # 结果返回
            return Response({'selected': selected})

        else:
            # 5. 未登录，保存cookie
            response = Response({'selected': selected})
            # 1、先获取cookie，判断原来是否写入过cookie
            cart_cookie = request.COOKIES.get('cart_cookie', None)
            if cart_cookie:
                # 2、写入过。解密.cart = {10: {‘count’:2, selected: True}
                cart = pickle.loads(base64.b64decode(cart_cookie))
                # 3. 更新所有数据
                for sku_id, data in cart.items():
                    data['selected'] = selected

                # 4. 加密操作
                cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
                # 5. 写入cookie
                response.set_cookie('cart_cookie', cart_cookie, max_age=60*60*24)

            return response