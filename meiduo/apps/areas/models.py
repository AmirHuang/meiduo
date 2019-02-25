from django.db import models


class Area(models.Model):
    """
    行政区划
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True,
                               blank=True, verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name_plural = verbose_name = '行政区划'

    def __str__(self):
        return self.name

# area.subs 通过该属性，可以获取相关的多数集合的数据(下属的下级规划区域)
# 默认是通过类名_set进行查询，通过指明related_name参数后，直接通过参数的数据来查询
