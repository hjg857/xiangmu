"""
URL configuration for schools app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import send_contact_email,submit_collaboration

urlpatterns = [
    # 账号申请 - 公开接口
    path('application/submit/', views.create_application, name='create_application'),
    path('application/<int:application_id>/status/', views.get_application_status, name='get_application_status'),
    path('application/check-by-email/', views.check_application_by_email, name='check_application_by_email'),
    
    # 账号申请 - 管理员接口
    path('applications/', views.list_applications, name='list_applications'),
    path('applications/<int:application_id>/approve/', views.approve_application, name='approve_application'),
    path('applications/<int:application_id>/reject/', views.reject_application, name='reject_application'),
    path('schools/import/', views.import_schools, name='import_schools'),
    
    # 学校信息
    path('list/', views.list_schools, name='list_schools'),
    path('<int:school_id>/delete/', views.delete_school, name='delete_school'),
    path('school/info/', views.get_school_info, name='get_school_info'),
    path('school/update/', views.update_school_info, name='update_school_info'),
    path('school/update-count/', views.update_school_info_count, name='update_school_info'),
    path('send-email/', send_contact_email, name='send_contact_email'),
    path('contact-collaboration/', submit_collaboration),
]
