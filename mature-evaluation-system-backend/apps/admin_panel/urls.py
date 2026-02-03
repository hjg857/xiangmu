"""
URL configuration for admin_panel app
"""
from django.urls import path
from . import views

urlpatterns = [
    # 申请管理
    path('applications/', views.get_application_list, name='admin_application_list'),
    
    # 内容管理（管理员接口）
    path('content/<str:page_key>/', views.update_page_content, name='update_page_content'),
    
    # 实践动态管理（管理员接口）
    path('news/', views.create_news, name='create_news'),
    path('news/<int:pk>/', views.update_news, name='update_news'),
    path('news/<int:pk>/delete/', views.delete_news, name='delete_news'),
    path('news/upload-image/', views.upload_news_image, name='upload_news_image'),
]
