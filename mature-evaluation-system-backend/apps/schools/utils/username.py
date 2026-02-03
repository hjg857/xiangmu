# apps/schools/utils/username.py
import random
import string

from django.contrib.auth import get_user_model

try:
    from pypinyin import lazy_pinyin
except ImportError:
    lazy_pinyin = None

User = get_user_model()


def _name_initials(name: str) -> str:
    """学校名称拼音首字母（大写）。没装 pypinyin 时做兜底。"""
    name = (name or "").strip()
    if not name:
        return "SCH"

    if lazy_pinyin:
        letters = "".join(
            p[0].upper()
            for p in lazy_pinyin(name)
            if p and p[0].isalpha()
        )
        return letters or "SCH"

    # 兜底：取字母数字前4个
    letters = "".join([c for c in name if c.isalnum()])[:4].upper()
    return letters or "SCH"


def gen_school_username(name: str) -> str:
    """规则：学校名称首字母（大写） + 6位随机大写字母数字"""
    head = _name_initials(name)
    tail = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{head}{tail}"


def gen_unique_school_username(name: str) -> str:
    """保证唯一"""
    for _ in range(20):
        u = gen_school_username(name)
        if not User.objects.filter(username=u).exists():
            return u
    raise RuntimeError("无法生成唯一 username，请稍后重试")
