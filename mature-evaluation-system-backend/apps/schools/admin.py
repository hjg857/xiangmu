"""
学校模块管理后台
"""
from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import School, AccountApplication
from apps.accounts.models import User
from utils.generators import generate_username, generate_strong_password
from .tasks import send_account_approval_email
from apps.regions.services import get_or_create_region_by_text
from apps.regions.models import Region


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    """学校管理"""
    list_display = ['name', 'school_type', 'province', 'city', 'district', 'contact_name', 'created_at']
    list_filter = ['school_type', 'province']
    search_fields = ['name', 'contact_name', 'contact_email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {'fields': ('user', 'name', 'school_type')}),
        ('地理位置', {'fields': ('province', 'city', 'district','region')}),
        ('联系信息', {'fields': ('contact_name', 'contact_position', 'contact_phone', 'contact_email')}),
        ('其他信息', {'fields': ('website_url',)}),
    )
    
    readonly_fields = []


@admin.register(AccountApplication)
class AccountApplicationAdmin(admin.ModelAdmin):
    """账号申请管理"""
    list_display = ['school_name', 'contact_name', 'status', 'applied_at', 'reviewed_at']
    list_filter = ['status', 'school_type', 'applied_at']
    search_fields = ['school_name', 'contact_name', 'contact_email']
    ordering = ['-applied_at']
    actions = ['approve_applications', 'reject_applications']
    
    fieldsets = (
        ('学校信息', {'fields': ('school_name', 'school_type', 'province', 'city', 'district')}),
        ('联系信息', {'fields': ('contact_name', 'contact_position', 'contact_phone', 'contact_email')}),
        ('审批信息', {'fields': ('status', 'reject_reason', 'reviewed_by', 'reviewed_at')}),
    )
    
    readonly_fields = ['applied_at', 'reviewed_at', 'reviewed_by']
    
    def approve_applications(self, request, queryset):
        """批量审批通过"""
        success_count = 0
        error_count = 0
        
        for application in queryset:
            if application.status != 'pending':
                self.message_user(
                    request,
                    f'申请 {application.school_name} 已处理，跳过',
                    level=messages.WARNING
                )
                continue
            
            try:
                with transaction.atomic():
                    # 生成用户名和密码
                    username = generate_username(application.school_name)
                    password = generate_strong_password()
                    
                    # 创建用户
                    user = User.objects.create_user(
                        username=username,
                        email=application.contact_email,
                        password=password,
                        role='school'
                    )
                    
                    # 创建学校记录
                    School.objects.create(
                        user=user,
                        name=application.school_name,
                        school_type=application.school_type,
                        province=application.province,
                        city=application.city,
                        district=application.district,
                        contact_name=application.contact_name,
                        contact_position=application.contact_position,
                        contact_phone=application.contact_phone,
                        contact_email=application.contact_email
                    )
                    
                    # 更新申请状态
                    application.status = 'approved'
                    application.reviewed_by = request.user
                    application.reviewed_at = timezone.now()
                    application.save()
                    
                    # 异步发送邮件
                    send_account_approval_email.delay(
                        username=username,
                        password=password,
                        email=application.contact_email,
                        school_name=application.school_name
                    )
                    
                    success_count += 1
                    
                    self.message_user(
                        request,
                        f'✓ {application.school_name} 审批成功！用户名：{username}，邮件已发送',
                        level=messages.SUCCESS
                    )
                    
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f'✗ {application.school_name} 审批失败：{str(e)}',
                    level=messages.ERROR
                )
        
        if success_count > 0:
            self.message_user(
                request,
                f'成功审批 {success_count} 个申请',
                level=messages.SUCCESS
            )
        
        if error_count > 0:
            self.message_user(
                request,
                f'失败 {error_count} 个申请',
                level=messages.ERROR
            )
    
    approve_applications.short_description = '✓ 审批通过选中的申请'
    
    def reject_applications(self, request, queryset):
        """批量拒绝"""
        count = 0
        for application in queryset:
            if application.status == 'pending':
                application.status = 'rejected'
                application.reject_reason = '管理员拒绝'
                application.reviewed_by = request.user
                application.reviewed_at = timezone.now()
                application.save()
                count += 1
        
        self.message_user(
            request,
            f'已拒绝 {count} 个申请',
            level=messages.WARNING
        )
    
    reject_applications.short_description = '✗ 拒绝选中的申请'
