"""
评估系统URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminDashboardStatsView, AdminAssessmentListView, AdminProvinceSummaryView
from . import views

router = DefaultRouter()
router.register(r'assessments', views.AssessmentViewSet, basename='assessment')

urlpatterns = [
    path('dashboard-stats/', AdminDashboardStatsView.as_view(), name='admin_stats'),
    path('province-summary/', AdminProvinceSummaryView.as_view(), name='province_summary'),
    path('assessment-list/', AdminAssessmentListView.as_view(), name='admin_assessments'),
    path('', include(router.urls)),

]
