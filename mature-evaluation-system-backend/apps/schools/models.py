"""
学校相关模型
"""
from django.db import models
from django.conf import settings
from apps.regions.models import Region


class School(models.Model):
    """学校模型"""
    
    SCHOOL_TYPE_CHOICES = [
        ('primary', '小学'),
        ('junior', '初中'),
        ('senior', '高中'),
        ('nine_year', '九年一贯制'),
        ('twelve_year', '十二年一贯制'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='school',
        verbose_name='关联用户'
    )
    name = models.CharField('学校全称', max_length=200)
    school_type = models.CharField('学校类型', max_length=50, choices=SCHOOL_TYPE_CHOICES)
    province = models.CharField('省份', max_length=50)
    city = models.CharField('城市', max_length=50)
    district = models.CharField('区县', max_length=50, blank=True)
    code = models.CharField('学校编码', max_length=64, unique=True, null=True, blank=True)
    region = models.ForeignKey(
        Region,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='schools',
        verbose_name='所属区县'
    )
    contact_name = models.CharField('联系人姓名', max_length=50)
    contact_position = models.CharField('联系人职务', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    contact_email = models.EmailField('联系邮箱')
    website_url = models.URLField('学校官网', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)


    class Meta:
        db_table = 'school'
        verbose_name = '学校'
        verbose_name_plural = '学校'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['school_type']),
            models.Index(fields=['province', 'city', 'district']),
        ]
    
    def __str__(self):
        return self.name


class AccountApplication(models.Model):
    """账号申请模型"""
    
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    school_name = models.CharField('学校全称', max_length=200)
    school_type = models.CharField('学校类型', max_length=50)
    province = models.CharField('省份', max_length=50)
    city = models.CharField('城市', max_length=50)
    district = models.CharField('区县', max_length=50, blank=True)
    district_code = models.CharField('区划代码', max_length=10, blank=True, null=True)
    contact_name = models.CharField('联系人姓名', max_length=50)
    contact_position = models.CharField('联系人职务', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    contact_email = models.EmailField('联系邮箱')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    reject_reason = models.TextField('拒绝原因', blank=True)
    applied_at = models.DateTimeField('申请时间', auto_now_add=True)
    reviewed_at = models.DateTimeField('审批时间', null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications',
        verbose_name='审批人'
    )
    
    class Meta:
        db_table = 'account_application'
        verbose_name = '账号申请'
        verbose_name_plural = '账号申请'
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.school_name} - {self.get_status_display()}"



