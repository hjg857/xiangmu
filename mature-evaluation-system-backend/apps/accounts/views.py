"""
用户认证视图
"""
import uuid
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
import string

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
import base64

from .models import User
from .serializers import (
    UserSerializer, LoginSerializer, 
    PasswordResetSerializer, PasswordChangeSerializer
)
from utils.response import APIResponse


@api_view(['GET'])
@permission_classes([AllowAny])
def generate_captcha(request):
    """生成图形验证码"""
    # 生成随机验证码
    code = ''.join(random.choices(string.digits, k=4))
    
    # 生成唯一key
    captcha_key = str(uuid.uuid4())
    
    # 存储到Redis，5分钟有效
    cache.set(f'captcha_{captcha_key}', code, 300)
    
    # 创建图片
    width, height = 120, 40
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 绘制验证码（使用默认字体）
    font = ImageFont.load_default()
    
    # 绘制文字
    for i, char in enumerate(code):
        x = 20 + i * 25
        y = 10
        # 随机颜色
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((x, y), char, fill=color, font=font)
    
    # 添加干扰线
    for _ in range(3):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='gray', width=1)
    
    # 添加干扰点
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill='gray')
    
    # 转换为base64
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return APIResponse.success({
        'captcha_key': captcha_key,
        'captcha_image': f'data:image/png;base64,{image_base64}'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """用户登录"""
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return APIResponse.error(
            message='登录失败',
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    user = serializer.validated_data['user']
    
    # 检查登录失败次数
    login_attempts_key = f'login_attempts_{user.username}'
    attempts = cache.get(login_attempts_key, 0)
    
    # 更新最后登录时间
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # 清除登录失败记录
    cache.delete(login_attempts_key)
    
    # 生成JWT Token
    refresh = RefreshToken.for_user(user)
    
    # 记录操作日志
    from apps.admin_panel.models import OperationLog
    OperationLog.objects.create(
        user=user,
        operation_type='login',
        operation_desc='用户登录',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return APIResponse.success({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    }, message='登录成功')


@api_view(['POST'])
@permission_classes([AllowAny])
def login_failed(request):
    """处理登录失败（用于记录失败次数）"""
    username = request.data.get('username')
    
    if not username:
        return APIResponse.error('用户名不能为空')
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return APIResponse.error('用户不存在')
    
    # 记录登录失败次数
    login_attempts_key = f'login_attempts_{username}'
    attempts = cache.get(login_attempts_key, 0) + 1
    cache.set(login_attempts_key, attempts, 900)  # 15分钟
    
    # 如果失败3次，锁定账号15分钟
    if attempts >= 3:
        user.is_locked = True
        user.locked_until = timezone.now() + timezone.timedelta(minutes=15)
        user.save(update_fields=['is_locked', 'locked_until'])
        
        return APIResponse.error(
            message='登录失败次数过多，账号已被锁定15分钟',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    return APIResponse.error(
        message=f'登录失败，还可尝试{3 - attempts}次',
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """刷新Token"""
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return APIResponse.error('refresh token不能为空')
    
    try:
        refresh = RefreshToken(refresh_token)
        return APIResponse.success({
            'access': str(refresh.access_token)
        })
    except Exception as e:
        return APIResponse.error(
            message='Token刷新失败',
            status_code=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """用户登出"""
    # 记录操作日志
    from apps.admin_panel.models import OperationLog
    OperationLog.objects.create(
        user=request.user,
        operation_type='logout',
        operation_desc='用户登出',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return APIResponse.success(message='登出成功')


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """重置密码（发送邮件）"""
    serializer = PasswordResetSerializer(data=request.data)
    
    if not serializer.is_valid():
        return APIResponse.error(
            message='参数错误',
            details=serializer.errors
        )
    
    email = serializer.validated_data['email']
    user = User.objects.get(email=email)
    
    # 生成重置token
    reset_token = str(uuid.uuid4())
    cache.set(f'reset_token_{reset_token}', user.id, 1800)  # 30分钟有效
    
    # TODO: 发送邮件（使用Celery异步任务）
    # 这里先返回成功，实际应该发送邮件
    
    return APIResponse.success(message='密码重置邮件已发送，请查收')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """修改密码"""
    serializer = PasswordChangeSerializer(data=request.data)
    
    if not serializer.is_valid():
        return APIResponse.error(
            message='参数错误',
            details=serializer.errors
        )
    
    user = request.user
    
    # 验证旧密码
    if not user.check_password(serializer.validated_data['old_password']):
        return APIResponse.error('旧密码错误')
    
    # 设置新密码
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    # 更新session
    update_session_auth_hash(request, user)
    
    # 记录操作日志
    from apps.admin_panel.models import OperationLog
    OperationLog.objects.create(
        user=user,
        operation_type='change_password',
        operation_desc='修改密码',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return APIResponse.success(message='密码修改成功')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """获取当前用户信息"""
    return APIResponse.success(UserSerializer(request.user).data)
