"""
生成器工具函数
"""
import random
import string
from pypinyin import lazy_pinyin


def generate_username(school_name, phone_number=None):
    """
    生成用户名：学校拼音首字母 + 完整电话号码
    例如：北京市第一中学 + 13812345678 -> bjsdyzx13812345678
    """
    # 获取学校名称拼音首字母
    pinyin_list = lazy_pinyin(school_name)
    initials = ''.join([py[0] for py in pinyin_list if py])
    
    # 使用完整电话号码，如果没有电话号码则使用随机数字
    if phone_number:
        suffix = phone_number
    else:
        suffix = ''.join(random.choices(string.digits, k=11))
    
    return f"{initials}{suffix}".lower()


def generate_strong_password(length=12):
    """
    生成强密码：包含大小写字母、数字和特殊字符
    """
    # 确保至少包含每种类型的字符
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice('!@#$%^&*'),
    ]
    
    # 填充剩余长度
    all_chars = string.ascii_letters + string.digits + '!@#$%^&*'
    password.extend(random.choices(all_chars, k=length - 4))
    
    # 打乱顺序
    random.shuffle(password)
    
    return ''.join(password)


def generate_verification_code(length=4):
    """
    生成数字验证码
    """
    return ''.join(random.choices(string.digits, k=length))
