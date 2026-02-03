"""
学校模块异步任务
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_account_approval_email(username, password, email, school_name):
    """
    发送账号审批通过邮件
    """
    subject = '【数据文化成熟度评估系统】账号审批通过通知'
    
    message = f"""尊敬的 {school_name} 用户：

您好！

您的账号申请已通过审核，以下是您的登录信息：

登录地址：{settings.FRONTEND_URL}/login
用户名：{username}
密码：{password}

祝 工作顺利，万事如意！

苏师YangTeam

此邮件由系统自动发送，请勿回复

======================================================

温馨提示：

1、请妥善保管您的账号信息
2、建议首次登录后及时修改密码
3、如有任何问题，请联系管理员

联系人：曾老师
电  话：18252169610
邮  件：a18390917485@163.com
邮  编：221116
地  址：江苏省徐州市铜山新区上海路101号

======================================================"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return f'邮件已发送至 {email}'
    except Exception as e:
        return f'邮件发送失败: {str(e)}'
