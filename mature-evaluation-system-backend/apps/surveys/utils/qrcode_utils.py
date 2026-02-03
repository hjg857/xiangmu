import hashlib
from io import BytesIO

import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def _hash_url(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def generate_qrcode_and_save(url: str, prefix: str = "survey") -> str:
    """
    输入url生成二维码PNG保存到storage，返回可访问URL（/media/... 或 OSS URL）
    带缓存：同一url不会重复生成
    """
    url_hash = _hash_url(url)
    filename = f"qrcodes/{prefix}_{url_hash}.png"

    if default_storage.exists(filename):
        return default_storage.url(filename)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    default_storage.save(filename, ContentFile(buf.read()))
    return default_storage.url(filename)
