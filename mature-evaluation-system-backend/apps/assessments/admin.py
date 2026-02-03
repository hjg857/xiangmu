"""
评估模块管理后台
"""
from django.contrib import admin
from .models import (
    Assessment, InstitutionAssessment, BehaviorAssessment,
    AssetAssessment, TechnologyAssessment
)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """评估记录管理"""
    list_display = ['school', 'status', 'total_score', 'maturity_level', 'started_at', 'completed_at']
    list_filter = ['status', 'maturity_level', 'started_at']
    search_fields = ['school__name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {'fields': ('school', 'status')}),
        ('得分信息', {'fields': ('literacy_score', 'institution_score', 'behavior_score', 'asset_score', 'technology_score', 'total_score')}),
        ('评估结果', {'fields': ('maturity_level', 'report_file')}),
        ('时间信息', {'fields': ('started_at', 'completed_at')}),
    )
    
    readonly_fields = ['started_at']


@admin.register(InstitutionAssessment)
class InstitutionAssessmentAdmin(admin.ModelAdmin):
    """数据制度评估管理"""
    list_display = ['assessment', 'has_leadership_group', 'has_data_staff', 'fulltime_staff_count', 'has_clear_responsibilities']
    search_fields = ['assessment__school__name']


@admin.register(BehaviorAssessment)
class BehaviorAssessmentAdmin(admin.ModelAdmin):
    """数据行为评估管理"""
    list_display = ['assessment', 'teacher_login_freq', 'student_login_freq', 'visit_count', 'created_at']
    search_fields = ['assessment__school__name']


@admin.register(AssetAssessment)
class AssetAssessmentAdmin(admin.ModelAdmin):
    """数据资产评估管理"""
    list_display = ['assessment', 'created_at']
    search_fields = ['assessment__school__name']


@admin.register(TechnologyAssessment)
class TechnologyAssessmentAdmin(admin.ModelAdmin):
    """数据技术评估管理"""
    list_display = ['assessment', 'data_center_standard', 'has_data_platform', 'security_certified_count', 'created_at']
    search_fields = ['assessment__school__name']
