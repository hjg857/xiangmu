# apps/regions/email_utils.py
import os

from django.conf import settings
from django.core.mail import send_mail

def send_school_account_email(*, school_name: str, to_email: str, username: str, password: str) -> bool:
    try:
        subject = "【中小学数据文化成熟度评估监测系统】账号创建通知"
        message = f"""尊敬的 {school_name} 用户：

您好！

您的学校账号已创建成功，以下是您的登录信息：

登录地址：{settings.FRONTEND_URL}
用户名：{username}
密码：{password}
======================================================
智能学习与评价江苏省产业技术工程化中心
邮箱:2020250606@jsnu.edu.cn
地址:江苏省徐州市铜山新区上海路101号
此邮件由系统自动发送，请勿回复
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
