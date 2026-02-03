"""
管理员功能模块管理后台
"""
from django.contrib import admin
from .models import OperationLog, SystemConfig, ContentPage


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    """操作日志管理"""
    list_display = ['user', 'operation_type', 'operation_desc', 'ip_address', 'created_at']
    list_filter = ['operation_type', 'created_at']
    search_fields = ['user__username', 'operation_desc']
    ordering = ['-created_at']
    readonly_fields = ['user', 'operation_type', 'operation_desc', 'ip_address', 'user_agent', 'created_at']
    
    def has_add_permission(self, request):
        """禁止手动添加日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改日志"""
        return False


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    """系统配置管理"""
    list_display = ['config_key', 'config_type', 'description', 'updated_at']
    list_filter = ['config_type']
    search_fields = ['config_key', 'description']
    ordering = ['config_key']


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    """内容页面管理"""
    list_display = ['title', 'page_key', 'order', 'is_published', 'updated_at']
    list_filter = ['page_key', 'is_published']
    search_fields = ['title', 'content']
    ordering = ['order']
