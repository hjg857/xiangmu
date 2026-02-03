"""
评估系统URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'assessments', views.AssessmentViewSet, basename='assessment')

urlpatterns = [
    path('', include(router.urls)),
]
