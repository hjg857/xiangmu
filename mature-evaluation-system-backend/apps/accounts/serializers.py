"""
用户认证序列化器
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'school_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'school_name']
    
    def get_school_name(self, obj):
        """获取学校名称"""
        if hasattr(obj, 'school') and obj.school:
            return obj.school.name
        return None


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(required=True, help_text='用户名')
    password = serializers.CharField(required=True, write_only=True, help_text='密码')
    captcha_key = serializers.CharField(required=True, help_text='验证码key')
    captcha_code = serializers.CharField(required=True, help_text='验证码')
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        captcha_key = attrs.get('captcha_key')
        captcha_code = attrs.get('captcha_code')
        
        # 验证验证码
        from django.core.cache import cache
        cached_code = cache.get(f'captcha_{captcha_key}')
        
        if not cached_code:
            raise serializers.ValidationError('验证码已过期，请刷新')
        
        if cached_code.lower() != captcha_code.lower():
            raise serializers.ValidationError('验证码错误')
        
        # 删除已使用的验证码
        cache.delete(f'captcha_{captcha_key}')
        
        # 验证用户名和密码
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        
        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')
        
        # 检查账号是否被锁定
        if user.check_locked():
            raise serializers.ValidationError(f'账号已被锁定，请稍后再试')
        
        attrs['user'] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """密码重置序列化器"""
    email = serializers.EmailField(required=True, help_text='注册邮箱')
    
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('该邮箱未注册')
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(required=True, write_only=True, help_text='旧密码')
    new_password = serializers.CharField(required=True, write_only=True, help_text='新密码')
    confirm_password = serializers.CharField(required=True, write_only=True, help_text='确认密码')
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('两次输入的密码不一致')
        
        if len(attrs['new_password']) < 8:
            raise serializers.ValidationError('密码长度至少为8位')
        
        return attrs
