# apps/regions/email_utils.py
import os

from django.conf import settings
from django.core.mail import send_mail

def send_school_account_email(*, school_name: str, to_email: str, username: str, password: str) -> bool:
    try:
        subject = "【数据文化成熟度评估系统】账号创建通知"
        message = f"""尊敬的 {school_name} 用户：

您好！

您的学校账号已创建成功，以下是您的登录信息：

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
电 话：18252169610 
邮 件：a18390917485@163.com 
邮 编：221116 
地 址：江苏省徐州市铜山新区上海路101号 
======================================================
"""
        # ✅ 关键1：测试阶段先 fail_silently=False，这样才能看到错误原因
        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=(settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER),
            recipient_list=[to_email],
            fail_silently=False,
        )
        ok = (sent_count == 1)
        print(f"[mail] sent_count={sent_count} ok={ok} to={to_email}")
        return ok
    except Exception as e:
        # ✅ 关键2：失败要打印原因（线上可换 logger）
        import traceback
        print(f"[mail] 错误详情: {str(e)}")
        traceback.print_exc()
        return False
