"""
问卷模块管理后台
"""
from django.contrib import admin
from .models import SurveyTemplate, SurveyQuestion, SurveyInstance, SurveyResponse


class SurveyQuestionInline(admin.TabularInline):
    """问卷题目内联"""
    model = SurveyQuestion
    extra = 1
    fields = ['question_text', 'question_type', 'order', 'is_required']


@admin.register(SurveyTemplate)
class SurveyTemplateAdmin(admin.ModelAdmin):
    """问卷模板管理"""
    list_display = ['title', 'survey_type', 'is_active', 'created_at']
    list_filter = ['survey_type', 'is_active']
    search_fields = ['title']
    inlines = [SurveyQuestionInline]


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    """问卷题目管理"""
    list_display = ['template', 'question_text', 'question_type', 'order', 'is_required']
    list_filter = ['template', 'question_type']
    ordering = ['template', 'order']


@admin.register(SurveyInstance)
class SurveyInstanceAdmin(admin.ModelAdmin):
    """问卷实例管理"""
    list_display = ['assessment', 'template', 'target_count', 'collected_count', 'is_active', 'created_at']
    list_filter = ['template', 'is_active']
    search_fields = ['assessment__school__name']
    readonly_fields = ['uuid']


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    """问卷回答管理"""
    list_display = ['instance', 'ip_address', 'submitted_at']
    list_filter = ['submitted_at']
    search_fields = ['instance__assessment__school__name']
    readonly_fields = ['submitted_at']
