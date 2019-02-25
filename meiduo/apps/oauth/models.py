from django.db import models

from utils.models import BaseModel


class OAuthUser(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    openid = models.CharField(db_index=True, max_length=64)

    class Meta:
        db_table = 'tb_oauth'
        verbose_name = verbose_name_plural = 'QQ用户'


