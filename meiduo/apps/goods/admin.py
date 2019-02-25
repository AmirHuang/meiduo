from django.contrib import admin
from celery_tasks.static_html.tasks import generate_static_list_search_html
from . import models


class GoodsAdmin(admin.ModelAdmin):
    # 商品ｓｐｕ表的后台管理器
    list_display = ['id', 'name']

    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_list_search_html.delay()

    def delete_model(self, request, obj):
        generate_static_list_search_html.delay()


admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods, GoodsAdmin)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)
