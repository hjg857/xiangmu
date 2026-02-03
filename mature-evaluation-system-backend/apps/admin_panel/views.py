"""
管理员功能视图
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q

from apps.schools.models import AccountApplication
from apps.schools.serializers import AccountApplicationSerializer
from .models import ContentPage, News
from .serializers import ContentPageSerializer, NewsSerializer
from utils.response import APIResponse


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_application_list(request):
    """获取申请列表（管理员）"""
    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以访问',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    # 获取查询参数
    school_type = request.GET.get('school_type', '')
    app_status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # 构建查询
    queryset = AccountApplication.objects.all().order_by('-applied_at')
    
    if school_type:
        queryset = queryset.filter(school_type=school_type)
    
    if app_status:
        queryset = queryset.filter(status=app_status)
    
    if search:
        queryset = queryset.filter(
            Q(school_name__icontains=search) |
            Q(contact_name__icontains=search) |
            Q(contact_email__icontains=search)
        )
    
    # 分页
    paginator = PageNumberPagination()
    paginator.page_size = int(request.GET.get('page_size', 20))
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = AccountApplicationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = AccountApplicationSerializer(queryset, many=True)
    return APIResponse.success(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_page_content(request, page_key):
    """获取页面内容（公开接口）"""
    try:
        content_page = ContentPage.objects.get(page_key=page_key, is_published=True)
        serializer = ContentPageSerializer(content_page)
        return APIResponse.success(serializer.data)
    except ContentPage.DoesNotExist:
        return APIResponse.error(
            message='页面不存在',
            status_code=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_page_content(request, page_key):
    """更新页面内容（管理员）"""
    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以访问',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    try:
        content_page = ContentPage.objects.get(page_key=page_key)
        serializer = ContentPageSerializer(content_page, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message='更新成功'
            )
        
        return APIResponse.error(
            message='数据验证失败',
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except ContentPage.DoesNotExist:
        return APIResponse.error(
            message='页面不存在',
            status_code=status.HTTP_404_NOT_FOUND
        )



# ==================== 实践动态相关视图 ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_news_list(request):
    """获取实践动态列表（公开接口）"""
    queryset = News.objects.filter(is_published=True)
    serializer = NewsSerializer(queryset, many=True, context={'request': request})
    return APIResponse.success(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_news_detail(request, pk):
    """获取实践动态详情（公开接口）"""
    try:
        news = News.objects.get(pk=pk, is_published=True)
        # 增加浏览次数
        news.view_count += 1
        news.save(update_fields=['view_count'])
        
        serializer = NewsSerializer(news, context={'request': request})
        return APIResponse.success(serializer.data)
    except News.DoesNotExist:
        return APIResponse.error(
            message='动态不存在',
            status_code=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_news(request):
    """创建实践动态（管理员）"""
    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以创建动态',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    serializer = NewsSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save(author=request.user)
        return APIResponse.success(
            data=serializer.data,
            message='创建成功',
            status_code=status.HTTP_201_CREATED
        )
    
    return APIResponse.error(
        message='数据验证失败',
        details=serializer.errors,
        status_code=status.HTTP_400_BAD_REQUEST
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_news(request, pk):
    """更新实践动态（管理员）"""
    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以更新动态',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    try:
        news = News.objects.get(pk=pk)
        serializer = NewsSerializer(news, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message='更新成功'
            )
        
        return APIResponse.error(
            message='数据验证失败',
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except News.DoesNotExist:
        return APIResponse.error(
            message='动态不存在',
            status_code=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_news(request, pk):
    """删除实践动态（管理员）"""
    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以删除动态',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    try:
        news = News.objects.get(pk=pk)
        news.delete()
        return APIResponse.success(message='删除成功')
    except News.DoesNotExist:
        return APIResponse.error(
            message='动态不存在',
            status_code=status.HTTP_404_NOT_FOUND
        )


class UploadNewsImageView(APIView):
    """上传实践动态图片（管理员）"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    # 明确指定只使用JWT认证，避免SessionAuthentication的CSRF检查
    authentication_classes = []
    
    def get_authenticators(self):
        """动态获取认证类，使用JWT认证"""
        from rest_framework_simplejwt.authentication import JWTAuthentication
        return [JWTAuthentication()]

    def post(self, request):
        """处理图片上传"""
        if not request.user.is_admin_user():
            return APIResponse.error(
                message='只有管理员可以上传图片',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        if 'image' not in request.FILES:
            return APIResponse.error('请选择要上传的图片')
        
        image = request.FILES['image']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image.content_type not in allowed_types:
            return APIResponse.error('只支持JPG、PNG、GIF、WEBP格式的图片')
        
        # 验证文件大小（最大5MB）
        if image.size > 5 * 1024 * 1024:
            return APIResponse.error('图片大小不能超过5MB')
        
        # 保存图片
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os
        from datetime import datetime
        
        # 生成文件名
        ext = os.path.splitext(image.name)[1]
        filename = f"news/images/{datetime.now().strftime('%Y/%m')}/{datetime.now().timestamp()}{ext}"
        
        # 保存文件
        path = default_storage.save(filename, ContentFile(image.read()))
        # 获取完整URL（适配OSS）
        url = default_storage.url(path)
        if not url.startswith('http'):
            url = request.build_absolute_uri(url)
        
        return APIResponse.success({
            'url': url,
            'path': path
        }, message='上传成功')

# 创建视图实例
upload_news_image = UploadNewsImageView.as_view()
