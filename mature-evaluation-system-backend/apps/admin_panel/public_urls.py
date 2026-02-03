"""
公开内容接口URL配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 内容管理（公开接口）
    path('content/<str:page_key>/', views.get_page_content, name='get_page_content'),
    
    # 实践动态（公开接口）
    path('news/', views.get_news_list, name='get_news_list'),
    path('news/<int:pk>/', views.get_news_detail, name='get_news_detail'),
]
