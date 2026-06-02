"""
学校模块序列化器
"""
from rest_framework import serializers
from .models import School, AccountApplication


class SchoolSerializer(serializers.ModelSerializer):
    """学校序列化器"""
    
    class Meta:
        model = School
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class SchoolAdminSerializer(serializers.ModelSerializer):
    """学校管理序列化器（包含评估信息）"""
    latest_assessment = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
        
    def get_latest_assessment(self, obj):
        """获取最新评估记录"""
        assessment = obj.assessments.order_by('-created_at').first()
        if assessment:
            return {
                'id': assessment.id,
                'status': assessment.status,
                'status_display': assessment.get_status_display(),
                'total_score': assessment.total_score,
                'maturity_level': assessment.maturity_level,
                'maturity_level_display': assessment.get_maturity_level_display(),
                'created_at': assessment.created_at
            }
        return None


class AccountApplicationSerializer(serializers.ModelSerializer):
    """账号申请序列化器"""

    apply_role_display = serializers.CharField(
        source='get_apply_role_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    display_name = serializers.SerializerMethodField()
    school_type_display = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = AccountApplication
        fields = [
            'id',

            # 新增：申请身份
            'apply_role',
            'apply_role_display',

            # 原有字段
            'school_name',
            'display_name',
            'school_type',
            'school_type_display',

            'province',
            'city',
            'district',
            'district_code',
            'location',

            'contact_name',
            'contact_position',
            'contact_phone',
            'contact_email',

            'status',
            'status_display',
            'reject_reason',
            'applied_at',
            'reviewed_at'
        ]

        read_only_fields = [
            'id',
            'status',
            'reject_reason',
            'applied_at',
            'reviewed_at'
        ]

    def get_display_name(self, obj):
        """列表展示名称"""
        if obj.apply_role == 'region_admin':
            return f'{obj.province}{obj.city}{obj.district}区域管理'
        return obj.school_name

    def get_school_type_display(self, obj):
        """列表展示类型"""
        if obj.apply_role == 'region_admin':
            return '区域管理员'
        return obj.school_type

    def get_location(self, obj):
        """所在地展示"""
        return f'{obj.province} {obj.city} {obj.district}'.strip()

    def validate_contact_phone(self, value):
        """验证手机号格式"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请输入有效的手机号码')
        return value


class AccountApplicationCreateSerializer(serializers.ModelSerializer):
    """账号申请创建序列化器"""
    
    class Meta:
        model = AccountApplication
        fields = [
            'school_name', 'school_type', 'province', 'city', 'district', 'district_code',
            'contact_name', 'contact_position', 'contact_phone', 'contact_email', 'apply_role'
        ]

    def validate_district_code(self, value):
        """验证 6 位区划代码"""
        if value and not (value.isdigit() and len(value) == 6):
            raise serializers.ValidationError('区划代码格式错误')
        return value

    def validate_contact_phone(self, value):
        """验证手机号格式"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请输入有效的手机号码')
        return value
    
    def validate_contact_email(self, value):
        """验证邮箱是否已被使用"""
        if AccountApplication.objects.filter(
            contact_email=value,
            status='pending'
        ).exists():
            raise serializers.ValidationError('该邮箱已有待审批的申请')
        
        from apps.accounts.models import User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('用户已注册账号，请勿重复申请')
        
        return value
