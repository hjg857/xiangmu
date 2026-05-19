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


class RegionReportSuggestionCache(models.Model):
    """
    区域报告 AI 建议缓存
    同一区域只保留一份最新建议。
    当区域报告数据发生变化时，通过 data_hash 自动重新生成。
    """

    region_code = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="区域编码"
    )

    region_name = models.CharField(
        max_length=128,
        blank=True,
        default="",
        verbose_name="区域名称"
    )

    data_hash = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name="数据指纹"
    )

    suggestions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="AI建议内容"
    )

    payload_snapshot = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="生成时的数据快照"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        db_table = "region_report_suggestion_cache"
        verbose_name = "区域报告AI建议缓存"
        verbose_name_plural = "区域报告AI建议缓存"

    def __str__(self):
        return f"{self.region_name or self.region_code} - {self.data_hash}"