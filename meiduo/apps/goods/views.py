from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import GoodsCategory
from rest_framework.generics import ListAPIView, CreateAPIView
from goods.models import GoodsCategory, SKU
from goods.serializers import CategoryListSerializers, SKUSearchSeriazliers
from .utils import PageNum
from rest_framework.filters import OrderingFilter
from drf_haystack.viewsets import HaystackViewSet
from .serializers import SKUHistorySeriazliers
from django_redis import get_redis_connection


class CategoryView(APIView):

    def get(self, request, pk):
        """
        从前端获取第三级分类id,
        并返回三级分类的名称
        """
        # 通过正则获取三级分类ｉｄ
        # 查询三分类信息
        cat3 = GoodsCategory.objects.get(id=pk)
        # 通过三级分类获取二级分类和一级分类
        cat2 = cat3.parent
        cat1 = cat2.parent

        return Response({
            "cat1": cat1.name,
            "cat2": cat2.name,
            "cat3": cat3.name,
        })


class CategoryListView(ListAPIView):
    """
    查询商品列表
    """
    serializer_class = CategoryListSerializers
    pagination_class = PageNum
    filter_backends = [OrderingFilter]  # 过滤排序属性
    # 指定排序字段
    ordering_filter = ["sale", 'create_time', 'price']

    def get_queryset(self):
        print('-self.kwargs:', self.kwargs)
        pk = self.kwargs['pk']
        return SKU.objects.filter(category_id=pk)


class SKUSearchViewSet(HaystackViewSet):
    index_models = [SKU]
    pagination_class = PageNum  # 分页属性
    serializer_class = SKUSearchSeriazliers


class SKUHistoryView(CreateAPIView):
    """
        保存和获取用户浏览历史记录
    """
    serializer_class = SKUHistorySeriazliers

    def get(self, request):
        # 1. 获取用户对象
        user = request.user
        # 2. 查询redis获取sku_id
        conn = get_redis_connection('history')
        sku_ids = conn.lrange('history_%s' % user.id, 0, 5)
        # 3. 根据sku_id查询商品对象
        skus = SKU.objects.filter(id__in=sku_ids)
        ser = CategoryListSerializers(skus, many=True)

        return Response(ser.data)
