# _*_ coding: utf-8 _*_
# @time     : 2018/12/06
# @Author   : Amir
# @Site     : 
# @File     : utils.py
# @Software : PyCharm

import base64
import re

import pickle
from django.contrib.auth.backends import ModelBackend
from django_redis import get_redis_connection

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
       自定义jwt认证成功返回数据
       """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


class UsernameMobileAuthBackend(ModelBackend):
    # 自定义用户验证(setting.py)
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            user.check_password(password)
            return user
        except Exception as e:
            return None


def merge_cart_cookie_to_redis(request, user, response):
    """
    合并请求用户的购物车数据，将未登录保存在cookie里的保存到redis中
    遇到cookie与redis中出现相同的商品时以cookie数据为主，覆盖redis中的数据
    :param request: 用户的请求对象
    :param user: 当前登录的用户
    :param response: 响应对象，用于清楚购物车cookie
    :return:
    """
    # 1. 获取cookie
    cart_cookie = request.COOKIE.get('cart_cookie', None)
    # 2. 判断cookie是否存在
    if cart_cookie is None:
        return response
    # 3. 存在则解密 cart = {10: {‘count’:2, selected: True}。cart = {}
    cart = pickle.loads(base64.b64decode(cart_cookie))
    # 4. 判断字典是否为空
    if not cart:
        return response
    # 5. 不为空 拆分数据
    # 6. 哈希 对应字典 {sku_id: count,sku_id2:count2}
    cart_dict = {}
    # 7. 集合 对应列表 选中[sku_id1, sku_id2]。未选中[sku_id3]
    sku_id = []  # 选中
    sku_id_none = []  # 未选中
    for skuid, data in cart.items():
        # 哈希
        cart_dict[sku_id] = data['count']
        if data['selected']:
            sku_id.append(skuid)
        else:
            sku_id_none.append(skuid)
    # 写入redis
    conn = get_redis_connection('carts')
    conn.hmset('cart_%s' % user.id, cart_dict)
    if sku_id:
        conn.sadd('cart_selected_%s' % user.id, *sku_id)
    if sku_id_none:
        conn.srem('cart_selected_%s' % user.id, *sku_id_none)
    # 9. 删除cookie
    response.delete_cookie('cart_cookie')

    return response

