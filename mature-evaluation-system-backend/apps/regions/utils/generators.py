# utils/generators.py
import secrets
import string
import re

USERNAME_RANDOM_LEN = 6
PASSWORD_LEN = 8

_USERNAME_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 避免易混淆字符
_PASSWORD_CHARS = string.ascii_letters + string.digits
USERNAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{5,30}$")

def school_name_initials(name: str, max_len: int = 4) -> str:
    """
    取学校名称“首字母”前缀：
    - 如果 name 含英文/数字：取每个单词/段的首字母
    - 纯中文：项目里如果你有 pypinyin 可以替换成拼音首字母；这里先做一个安全兜底 SCH
    """
    if not name:
        return "SCH"

    # 提取英文数字段
    parts = re.findall(r"[A-Za-z0-9]+", name)
    if parts:
        initials = "".join(p[0] for p in parts if p)
        initials = initials.upper()
        return (initials[:max_len] or "SCH")

    # 纯中文：如果你后续接 pypinyin，就在这里替换
    return "SCH"


def gen_school_username(name: str) -> str:
    prefix = school_name_initials(name, max_len=4)
    suffix = "".join(secrets.choice(_USERNAME_CHARS) for _ in range(USERNAME_RANDOM_LEN))
    return f"{prefix}{suffix}"


def gen_unique_school_username(name: str, user_model) -> str:
    """
    user_model: 传 User 类，避免循环 import
    """
    while True:
        u = gen_school_username(name)
        if not user_model.objects.filter(username=u).exists():
            return u


def gen_strong_password(length: int = PASSWORD_LEN) -> str:
    return "".join(secrets.choice(_PASSWORD_CHARS) for _ in range(length))
