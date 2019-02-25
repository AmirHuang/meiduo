from django.shortcuts import render
from django.conf import settings
from QQLoginTool.QQtool import OAuthQQ
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJSS
from .serializers import OauthSerializer


class OauthQQloginView(APIView):
    """
        构建ｑｑ的跳转链接
        """

    def get(self, request):
        # 1. 获取前端定义好的字符串数据
        state = request.query_params.get('next', None)
        # 2、判断前端是否传递字符串数据
        if not state:
            state = '/'
        # 3. 创建qq对象
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state=state)
        # 4. 构建跳转链接
        login_url = qq.get_qq_url()
        # 5. 返回结果
        return Response({'login_url': login_url})


class OauthView(APIView):
    def get(self, request):
        # 1. 获取前端传来的code值
        code = request.query_params.get('code', None)
        # 2. 判断前端是否传来了code值
        if not code:
            return Response({'error': '缺失code值'}, status=400)
        # 3. 通过code值获取access_token
        state = '/'
        qq = OAuthQQ(client_secret=settings.QQ_CLIENT_SECRET,
                     client_id=settings.QQ_CLIENT_ID,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state=state)
        access_token = qq.get_access_token(code)
        # 4. 通过access_token获取openid
        openid = qq.get_open_id(access_token)
        # 5. 判断openid是否绑定多个用户
        try:
            qq_user = OAuthUser.objects.get('openid')
        except:
            tjss = TJSS(settings.SECRET_KEY, 300)
            openid = tjss.dumps({'openid': openid}).decode()

            # 6. 未绑定 跳转到绑定页面
            return Response({'access_token': openid})
        else:
            # 7. 绑定过, 则生成jwt_token
            user = qq_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({
                "token": token,
                "username": user.username,
                "user_id": user.id,
            })

    def post(self, request):
        # 1. 获取前端数据
        data = request.data
        # 2. 验证数据
        ser = OauthSerializer(data=data)
        ser.is_valid()
        print(ser.errors)
        # 3. 绑定保存数据
        ser.save()
        # 4. 返回结果
        return Response(ser.data)



