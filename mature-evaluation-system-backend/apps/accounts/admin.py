"""
用户认证模块管理后台
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ['username', 'email', 'role', 'is_active', 'is_locked', 'created_at']
    list_filter = ['role', 'is_active', 'is_locked']
    search_fields = ['username', 'email']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email',)}),
        ('权限', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('锁定信息', {'fields': ('is_locked', 'locked_until')}),
        ('重要日期', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
