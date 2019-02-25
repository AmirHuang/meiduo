from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.generics import ListAPIView
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework.permissions import IsAuthenticated

from .models import Area
from users.models import Address
from .serializers import AreaSerializer, AddressesSerializer
from utils.dumpexcel import DataDumpView


# 通过继承扩展实现使用缓存
class AreaView(CacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取省份信息
    """
    # queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer

    def get_queryset(self):
        parent_id = self.request.GET.get('parent_id')
        print('---parent_id---', parent_id)
        if parent_id:
            return Area.objects.filter(parent_id=parent_id)
        else:
            print('------------------')
            return Area.objects.filter(parent=None)


class Area1View(ListAPIView):
    """
        获取市/区信息
        """
    serializer_class = AreaSerializer

    # 缓存得使用需要装饰器装饰在定义的方法上
    # @cache_response(timeout=60 * 60, cache='default')
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Area.objects.filter(parent_id=pk)


class AddressesView(viewsets.ModelViewSet):
    """
        保存新增地址
        """
    serializer_class = AddressesSerializer
    permission_classes = [IsAuthenticated, ]

    # # 重写get_queryset获取指定内容
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response({"addresses": serializer.data})

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class AreaDumpView(DataDumpView):
    """导出地址"""
    model = Area  # 要下载的表
    fields = '__all__'  # 要导出的字段
    exclude = []  # 导出时排除的字段
    order_field = 'id'  # 排序依据，必须指定
    limit = 30000  # 当不重构get_queryset方法时返回的记录条数
    sheet_size = 300  # 每个sheet的记录条数，默认是300
    file_name = 'area报表'  # 最终生成的文件名:订单报表.xls
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self, request):
        """一般来说需要重写这个方法指定要下载的文件记录"""
        return Area.objects.all()