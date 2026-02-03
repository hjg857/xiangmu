# apps/regions/serializers_create_school.py
from rest_framework import serializers

SCHOOL_TYPE_CHOICES = {"primary", "junior", "senior", "nine_year", "twelve_year"}


class RegionAdminCreateSchoolSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="学校账号初始密码（不少于8位）；不填则自动生成"
    )

    name = serializers.CharField(required=True)
    school_type = serializers.CharField(required=True)
    province = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    district = serializers.CharField(required=True)

    contact_name = serializers.CharField(required=True)
    contact_position = serializers.CharField(required=True)
    contact_phone = serializers.CharField(required=True)
    contact_email = serializers.EmailField(required=True)
