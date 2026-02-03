# apps/regions/services.py
import hashlib
from apps.regions.models import Region

def _gen_region_code(province: str, city: str, district: str) -> str:
    raw = f"{province}-{city}-{district}"
    return "R" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]

def get_or_create_region_by_text(province: str, city: str, district: str, code: str = None) -> Region:
    """
    优先按 code 查找 Region，若无 code 则按 (province, city, name=district) 查找。
    不存在就创建一个。
    """
    p = (province or "").strip()
    c = (city or "").strip()
    d = (district or "").strip()
    cd = (code or "").strip()

    # 场景 A：前端传了 code，这是最精准的
    if cd:
        region, created = Region.objects.get_or_create(
            code=cd,
            defaults={
                "province": p,
                "city": c,
                "name": d,
                "level": "district",
                "is_active": True,
            }
        )
        return region

    # 场景 B：没有 code（兼容旧数据或异常情况），按文字找
    if not (p and c and d):
        raise ValueError("province/city/district 不能为空，无法定位 Region")

    region, created = Region.objects.get_or_create(
        province=p,
        city=c,
        name=d,
        defaults={
            "code": _gen_region_code(p, c, d), # 只有没传 code 时才自动生成
            "level": "district",
            "is_active": True,
        }
    )
    return region
