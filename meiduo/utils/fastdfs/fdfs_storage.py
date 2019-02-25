# _*_ coding: utf-8 _*_
# @time     : 2018/12/08
# @Author   : Amir
# @Site     : 
# @File     : fdfs_storage.py.py
# @Software : PyCharm


from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client


@deconstructible
class FastDFSStorage(Storage):
    def __init__(self, base_url=None, client_conf=None):
        """
        初始化
        :param base_url: 用于构造图片完整路径使用，图片服务器的域名
        :param client_conf: FastDFS客户端配置文件的路径
        """
        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        # 保存图片数据
        client = Fdfs_client(self.client_conf)

        # 上传fastDFS  上传七牛
        ret = client.upload_by_buffer(content.read())

        # 判断结果
        if ret['Status'] != 'Upload successed.':
            raise Exception("upload file failed")

        # 获取file_id
        file_id = ret['Remote file_id']

        return file_id

    def url(self, name):

        # 拼接路径

        return self.base_url + name

    def exists(self, name):
        # 判断文件是否重复

        return False
