# apps/regions/models.py
from django.db import models

from config import settings


class Region(models.Model):
    LEVEL_CHOICES = [
        ('district', '区县'),
        # 以后可以扩展 city / province
    ]

    code = models.CharField(
        '行政区编码',
        max_length=20,
        unique=True
    )
    name = models.CharField(
        '区县名称',
        max_length=50
    )
    province = models.CharField(
        '省份',
        max_length=50
    )
    city = models.CharField(
        '城市',
        max_length=50
    )
    level = models.CharField(
        '层级',
        max_length=20,
        choices=LEVEL_CHOICES,
        default='district'
    )

    is_active = models.BooleanField('是否启用', default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    region_admin = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_region',
        verbose_name='区域管理员'
    )

    class Meta:
        db_table = 'region'
        verbose_name = '行政区'
        verbose_name_plural = '行政区'
        indexes = [
            models.Index(fields=['province', 'city', 'name']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f'{self.city}-{self.name}'
