"""
URL configuration for accounts app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('captcha/', views.generate_captcha, name='generate_captcha'),
    path('login/', views.login, name='login'),
    path('login-failed/', views.login_failed, name='login_failed'),
    path('logout/', views.logout, name='logout'),
    path('refresh/', views.refresh_token, name='refresh_token'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('change-password/', views.change_password, name='change_password'),
    path('current-user/', views.current_user, name='current_user'),
]
