"""
自定义验证器
"""
import re
from django.core.exceptions import ValidationError


def validate_phone(value):
    """验证手机号码"""
    pattern = r'^1[3-9]\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError('请输入有效的手机号码')


def validate_password_strength(value):
    """验证密码强度：至少8位，包含大小写字母、数字"""
    if len(value) < 8:
        raise ValidationError('密码长度至少为8位')
    
    if not re.search(r'[a-z]', value):
        raise ValidationError('密码必须包含小写字母')
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError('密码必须包含大写字母')
    
    if not re.search(r'\d', value):
        raise ValidationError('密码必须包含数字')
