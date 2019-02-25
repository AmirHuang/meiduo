# # _*_ coding: utf-8 _*_
# # @time     : 2018/12/04
# # @Author   : Amir
# # @Site     :
# # @File     : media_server.py
# # @Software : PyCharm
#
#
# import os
# from urllib.parse import unquote
#
# from django.views.static import serve
# from django.http.response import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
#
# from smaill_project import settings
#
#
# def remove_media_file(path):
#     """移除本地文件(要先urldecode)"""
#     full_path = os.path.join(settings.MEDIA_ROOT, unquote(path))
#     if os.path.exists(full_path):
#         os.remove(full_path)
#     return full_path
#
#
# def remove_db_recode(path):
#     # 移除数据库记录
#     from .models import Img
#     return Img.objects.filter(image=path).delete()
#
#
# def permission_check(request):
#     # 这个操作很危险，因此只有超管有权
#     if not request.user.is_superuser:
#         return JsonResponse({'code': -1, 'msg': 'Permission denied.'})
#
#
# def delete_media(serve):
#     def wrapper(request, path, *args, **kwargs):
#         if request.method == 'DELETE':
#             permission_check(request)
#             remove_media_file(path)
#             remove_db_recode(path)
#             return JsonResponse({'code': 0, 'msg': 'OK'})
#         return serve(request, path, *args, **kwargs)
#
#     return wrapper
#
#
# @csrf_exempt
# @delete_media
# def support_delete_serve(request, path, **kwargs):
#     # 通过装饰器返回一个可删除media资源的serve
#     return serve(request, path, **kwargs)
