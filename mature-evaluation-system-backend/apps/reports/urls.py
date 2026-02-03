from django.urls import path
from . import views

urlpatterns = [
    # 生成报告
    path('assessments/<int:assessment_id>/generate/', views.generate_report, name='generate_report'),

    # 查看报告数据（用于前端展示）
    path('assessments/<int:assessment_id>/data/', views.get_report_data, name='get_report_data'),

    # 下载报告PDF
    path('assessments/<int:assessment_id>/download/', views.download_report, name='download_report'),
]
