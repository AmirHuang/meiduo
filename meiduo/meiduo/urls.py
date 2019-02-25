"""meiduo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url
from goods import views

from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from areas.views import AddressesView, AreaView
from users.views import UserView, UserDetailView, UserLoginView


router = DefaultRouter()
router.register('address', AddressesView, base_name='address')

# user
router.register('user', UserView, base_name='user')

# user
router.register('users', UserDetailView, base_name='users')

# area
router.register('areaview', AreaView, base_name='areaview')

router.register("skus/search", views.SKUSearchViewSet, base_name="sku_search")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('ueditor/', include('DjangoUeditor.urls')),

    path('api-auth/', include('rest_framework.urls')),

    # drf文档，title自定义
    path('docs', include_docs_urls(title='Amir')),

    # users的url
    re_path(r'', include('users.urls')),

    # areas de url
    re_path(r'', include('areas.urls')),

    # goods 的 url
    path(r'', include('goods.urls')),

    # cart de url
    path('', include('carts.urls')),

    # oauth的url
    path('oauth/', include('oauth.urls')),

    re_path('^', include(router.urls)),

    # Django REST framework JWT提供了登录签发JWT的视图，可以直接使用
    # ps:但是默认的返回值仅有token，我们还需在返回值中增加username和user_id。
    path('authorizations/', UserLoginView.as_view()),

    # 添加ckeditor路由
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # orders 的 url
    path(r'', include('orders.urls')),


]
