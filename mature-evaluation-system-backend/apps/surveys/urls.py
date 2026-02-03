"""
问卷系统URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import publish_literacy_surveys
from . import views

router = DefaultRouter()
router.register(r'instances', views.SurveyInstanceViewSet, basename='survey-instance')

urlpatterns = [
    path('', include(router.urls)),
    
    # 公开接口：通过UUID获取问卷
    path('public/<uuid:uuid>/', views.get_survey_by_uuid, name='survey-public-get'),
    
    # 公开接口：提交问卷
    path('public/<uuid:uuid>/submit/', views.submit_survey, name='survey-public-submit'),
    
    # 获取某个评估的所有问卷实例
    path('assessment/<int:assessment_id>/', views.get_assessment_surveys, name='assessment-surveys'),

    path('assessments/<int:assessment_id>/literacy/publish/', publish_literacy_surveys),
]
