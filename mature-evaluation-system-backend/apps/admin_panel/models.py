"""
管理员功能相关模型
"""
from django.db import models
from django.conf import settings


class News(models.Model):
    """实践动态模型"""
    
    title = models.CharField('标题', max_length=200)
    summary = models.TextField('摘要', max_length=500)
    content = models.TextField('详细内容')
    cover_image = models.ImageField('封面图片', upload_to='news/covers/%Y/%m/', blank=True, null=True)
    publish_date = models.DateField('发布日期')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='news_articles',
        verbose_name='作者'
    )
    is_published = models.BooleanField('是否发布', default=True)
    view_count = models.IntegerField('浏览次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'news'
        verbose_name = '实践动态'
        verbose_name_plural = '实践动态'
        ordering = ['-publish_date', '-created_at']
        indexes = [
            models.Index(fields=['-publish_date']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return self.title


class OperationLog(models.Model):
    """操作日志模型"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='operation_logs',
        verbose_name='操作用户'
    )
    operation_type = models.CharField('操作类型', max_length=50)
    operation_desc = models.TextField('操作描述')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        db_table = 'operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['operation_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.operation_type} - {self.created_at}"


class SystemConfig(models.Model):
    """系统配置模型"""
    
    CONFIG_TYPE_CHOICES = [
        ('string', '字符串'),
        ('int', '整数'),
        ('float', '浮点数'),
        ('bool', '布尔值'),
        ('json', 'JSON'),
    ]
    
    config_key = models.CharField('配置键', max_length=100, unique=True)
    config_value = models.TextField('配置值')
    config_type = models.CharField('配置类型', max_length=20, choices=CONFIG_TYPE_CHOICES, default='string')
    description = models.TextField('配置说明')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'system_config'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['config_key']
    
    def __str__(self):
        return f"{self.config_key}: {self.config_value}"
    
    def get_value(self):
        """获取配置值（根据类型转换）"""
        if self.config_type == 'int':
            return int(self.config_value)
        elif self.config_type == 'float':
            return float(self.config_value)
        elif self.config_type == 'bool':
            return self.config_value.lower() in ('true', '1', 'yes')
        elif self.config_type == 'json':
            import json
            return json.loads(self.config_value)
        return self.config_value
    
    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        try:
            config = cls.objects.get(config_key=key, is_active=True)
            return config.get_value()
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_config(cls, key, value, config_type='string', description=''):
        """设置配置值"""
        import json
        
        # 转换值为字符串
        if config_type == 'json':
            value_str = json.dumps(value, ensure_ascii=False)
        else:
            value_str = str(value)
        
        config, created = cls.objects.update_or_create(
            config_key=key,
            defaults={
                'config_value': value_str,
                'config_type': config_type,
                'description': description
            }
        )
        return config


class ContentPage(models.Model):
    """内容页面模型"""
    
    PAGE_KEY_CHOICES = [
        ('about', '关于我们'),
        ('culture', '数据文化'),
        ('guide', '评估说明'),
        ('news', '实践动态'),
    ]
    
    page_key = models.CharField('页面标识', max_length=50, choices=PAGE_KEY_CHOICES, unique=True)
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    order = models.IntegerField('排序', default=0)
    is_published = models.BooleanField('是否发布', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'content_page'
        verbose_name = '内容页面'
        verbose_name_plural = '内容页面'
        ordering = ['order']
    
    def __str__(self):
        return self.title
