from django.shortcuts import render
from django.conf import settings
from django_redis import get_redis_connection
from rest_framework.views import APIView
from random import randint
from rest_framework.response import Response
from celery_tasks.sms.tasks import send_sms_code
from rest_framework import viewsets, mixins
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from itsdangerous import TimedJSONWebSignatureSerializer as TJSS
from rest_framework_jwt.views import ObtainJSONWebToken

from .serializers import UserSerialzier, UserDetailSerializer, UserUpdateSerializer
from .models import User
from .utils import merge_cart_cookie_to_redis


class SmsCode(APIView):

    def get(self, request, mobile):
        # 1.从前端获取手机号
        # 2.对手机号进行正则校验
        # 3.生成短信验证码
        sms_code = '%06d' % randint(0, 999999)
        print(sms_code)
        # 4.保存短信信息到ｒｅｄｉｓ数据中
        # 和redis数据库建立连接
        con = get_redis_connection('smscodes')
        flag = con.get('smscode_flag_%s' % mobile)
        print('----flag', flag)
        if flag:
            return Response({'error': '请求过于频繁'})
        # 生成管道对象
        p1 = con.pipeline()
        # 保存短信验证码到redis中
        p1.setex('smscode_%s' % mobile, 300, sms_code)
        # 设置请求时效标志
        p1.setex('smscode_flag_%s' % mobile, 60, 1)
        # 执行管道（连接缓存， 存入数据）
        p1.execute()
        # 使用celery异步发送短信
        result_dic = send_sms_code(sms_code, mobile)
        return Response(result_dic)


class UserNameView(APIView):
    def get(self, request, username):
        # 查找数据
        count = User.objects.filter(username=username).count()
        # 返回结果
        return Response({
            'count': count
        })


class MobileView(APIView):
    def get(self, request, mobile):
        # 查找数据
        count = User.objects.filter(mobile=mobile).count()
        # 返回结果
        return Response({
            'count': count
        })


class UserView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerialzier


class UserDetailView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = UserDetailSerializer
    # 权限指定， 只有被认证后的用户才可以访问
    permission_classes = [IsAuthenticated(), ]

    # 重写get_object方法，返回用户指定信息
    def get_object(self):
        return self.request.user


class UserUpdateView(UpdateAPIView):
    """
        绑定邮箱账号并发送邮件
        """
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user


class EmailVerifyView(APIView):
    """
    用户邮箱信息验证
    """
    def get(self, request):
        # 1. 从前端获取token
        token = request.query_params.get('token')
        # 2. 检查数据
        tjss = TJSS(settings.SECRET_KEY, 300)
        try:
            data = tjss.loads(token)
        except:
            return Response({'error': 'token无效'})
        # 3. 查询用户数据
        username = data.get('username')
        user = User.objects.get(username=username)

        # 4. 修改用户邮箱状态
        user.email_active = True
        user.save()
        return Response({'message': True})


class UserLoginView(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user

            # 合并购物车
            response = merge_cart_cookie_to_redis(request, user, response)
        return response
