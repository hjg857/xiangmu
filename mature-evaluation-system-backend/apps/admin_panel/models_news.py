"""
实践动态模型
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
