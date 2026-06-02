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

from apps.schools.models import AccountApplication, School
from apps.schools.serializers import AccountApplicationSerializer
from .models import ContentPage, News
from .serializers import ContentPageSerializer, NewsSerializer
from utils.response import APIResponse
from ..assessments.models import Assessment


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


from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_region_report_assessments(request):
    """
    超级管理员查看指定区域的区域评估报告数据

    支持：
    /api/admin/region-report/assessments/?region_id=1
    /api/admin/region-report/assessments/?province=江苏省&city=南京市&district=鼓楼区
    """
    if not request.user.is_admin_user():
        return Response(
            {"success": False, "message": "只有超级管理员可以访问"},
            status=403
        )

    region_id = (request.query_params.get("region_id") or "").strip()
    province = (request.query_params.get("province") or "").strip()
    city = (request.query_params.get("city") or "").strip()
    district = (request.query_params.get("district") or "").strip()

    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 1000))
    status_value = (request.query_params.get("status") or "completed").strip()

    if not region_id and not (province and city and district):
        return Response(
            {
                "success": False,
                "message": "请提供 region_id，或完整的 province、city、district"
            },
            status=400
        )

    school_qs = School.objects.all()

    if region_id:
        school_qs = school_qs.filter(region_id=region_id)
    else:
        school_qs = school_qs.filter(
            province=province,
            city=city,
            district=district
        )

    first_school = school_qs.first()

    # 没有学校也返回空报告结构，避免前端报错
    if first_school:
        region_data = {
            "id": first_school.region_id,
            "province": first_school.province,
            "city": first_school.city,
            "name": first_school.district,
        }
    else:
        region_data = {
            "id": region_id or "",
            "province": province,
            "city": city,
            "name": district,
        }

    assessment_qs = (
        Assessment.objects
        .select_related("school")
        .filter(school__in=school_qs)
        .order_by("-created_at")
    )

    if status_value:
        assessment_qs = assessment_qs.filter(status=status_value)

    paginator = Paginator(assessment_qs, page_size)
    page_obj = paginator.get_page(page)

    assessments = []

    for assessment in page_obj:
        school = assessment.school

        assessments.append({
            "id": assessment.id,
            "status": assessment.status,
            "maturity_level": assessment.maturity_level,

            "school": {
                "id": school.id,
                "name": school.name,
                "school_type": school.school_type,
                "province": school.province,
                "city": school.city,
                "district": school.district,
                "region_id": school.region_id,
            },

            "scores": {
                "total_score": str(assessment.total_score or 0),
                "literacy_score": str(assessment.literacy_score or 0),
                "institution_score": str(assessment.institution_score or 0),
                "behavior_score": str(assessment.behavior_score or 0),
                "asset_score": str(assessment.asset_score or 0),
                "technology_score": str(assessment.technology_score or 0),
            },

            "times": {
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M:%S") if assessment.created_at else "",
                "completed_at": assessment.completed_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(assessment, "completed_at", None) else "",
            }
        })

    completed_count = (
        Assessment.objects
        .filter(school__in=school_qs, status="completed")
        .count()
    )

    summary = {
        "school_count": school_qs.count(),
        "assessment_count": Assessment.objects.filter(school__in=school_qs).count(),
        "completed_count": completed_count,
        "report_count": completed_count,
    }

    return Response({
        "success": True,
        "data": {
            "region": region_data,
            "summary": summary,
            "assessments": assessments,
            "pagination": {
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
            }
        }
    })


import re
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from apps.accounts.models import User
from apps.schools.models import School
from apps.regions.models import Region
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_region_admin(request):
    """超级管理员创建单个区域管理员账号"""

    if not request.user.is_admin_user():
        return Response({
            'success': False,
            'message': '只有超级管理员可以操作'
        }, status=403)

    province = (request.data.get('province') or '').strip()
    city = (request.data.get('city') or '').strip()
    district = (request.data.get('district') or '').strip()

    contact_name = (request.data.get('contact_name') or '').strip()
    contact_position = (request.data.get('contact_position') or '').strip()
    contact_phone = (request.data.get('contact_phone') or '').strip()
    contact_email = (request.data.get('contact_email') or '').strip()

    username = (request.data.get('username') or '').strip()
    password = (request.data.get('password') or '').strip()

    missing = []

    if not province:
        missing.append('省份')
    if not city:
        missing.append('城市')
    if not district:
        missing.append('区县')
    if not contact_name:
        missing.append('联系人姓名')
    if not contact_position:
        missing.append('职务')
    if not contact_phone:
        missing.append('联系电话')
    if not contact_email:
        missing.append('联系邮箱')
    if not username:
        missing.append('用户名')
    if not password:
        missing.append('初始密码')

    if missing:
        return Response({
            'success': False,
            'message': f"必填项缺失：{'、'.join(missing)}"
        }, status=400)

    if not re.fullmatch(r'1[3-9]\d{9}', contact_phone):
        return Response({
            'success': False,
            'message': '联系电话格式不正确，请填写11位手机号'
        }, status=400)

    if not re.fullmatch(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', contact_email):
        return Response({
            'success': False,
            'message': '邮箱格式不正确'
        }, status=400)

    if not re.fullmatch(r'[A-Za-z0-9]+', username):
        return Response({
            'success': False,
            'message': '用户名只能包含数字或字母，不能包含特殊字符'
        }, status=400)

    if not re.fullmatch(r'[A-Za-z0-9]{8}', password):
        return Response({
            'success': False,
            'message': '初始密码必须为8位数字或字母组合'
        }, status=400)

    if User.objects.filter(username=username).exists():
        return Response({
            'success': False,
            'message': '用户名已存在，请更换用户名'
        }, status=400)

    if User.objects.filter(email=contact_email).exists():
        return Response({
            'success': False,
            'message': '该邮箱已被注册，请更换邮箱'
        }, status=400)

    # 防止同一区域重复创建区域管理员
    existing_region = Region.objects.filter(
        province=province,
        city=city,
        name=district
    ).first()

    if existing_region and User.objects.filter(
        role='region_admin',
        region=existing_region
    ).exists():
        return Response({
            'success': False,
            'message': f'{province}{city}{district}已存在区域管理员账号'
        }, status=400)

    try:
        with transaction.atomic():
            region, _ = Region.objects.get_or_create(
                province=province,
                city=city,
                name=district,
                defaults={
                    'code': f'{province}-{city}-{district}'
                }
            )

            user = User.objects.create_user(
                username=username,
                email=contact_email,
                password=password,
                role='region_admin',
                is_active=True,
                is_staff=False
            )

            # 如果 User 模型里有这些字段，就同步保存
            if hasattr(user, 'real_name'):
                user.real_name = contact_name

            if hasattr(user, 'phone'):
                user.phone = contact_phone

            if hasattr(user, 'region'):
                user.region = region

            if hasattr(user, 'is_locked'):
                user.is_locked = False

            if hasattr(user, 'locked_until'):
                user.locked_until = None

            user.save()

            # 如果你的 Region 模型里有管理员字段，也同步绑定
            if hasattr(region, 'admin_user'):
                region.admin_user = user

            if hasattr(region, 'contact_name'):
                region.contact_name = contact_name

            if hasattr(region, 'contact_position'):
                region.contact_position = contact_position

            if hasattr(region, 'contact_phone'):
                region.contact_phone = contact_phone

            if hasattr(region, 'contact_email'):
                region.contact_email = contact_email

            region.save()

        subject = '【中小学数据文化成熟度评估监测系统】区域管理员账号创建通知'
        message = f"""尊敬的 {contact_name}：

您好！

您的区域管理员账号已创建成功，以下是登录信息：

管理区域：{province}{city}{district}
登录地址：{settings.FRONTEND_URL}
用户名：{username}
初始密码：{password}

请妥善保管账号信息，并建议首次登录后及时修改密码。

此邮件由系统自动发送，请勿回复。
"""

        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [contact_email],
                fail_silently=True
            )
        except Exception:
            pass

        return Response({
            'success': True,
            'message': '区域管理员账号创建成功',
            'data': {
                'region_id': region.id,
                'username': username,
                'province': province,
                'city': city,
                'district': district
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'创建失败：{str(e)}'
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_region_admin(request, user_id):
    """超级管理员删除区域管理员账号"""

    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以操作',
            status_code=status.HTTP_403_FORBIDDEN
        )

    try:
        user = User.objects.get(id=user_id, role='region_admin')
    except User.DoesNotExist:
        return APIResponse.error(
            message='区域管理员账号不存在',
            status_code=status.HTTP_404_NOT_FOUND
        )

    try:
        with transaction.atomic():
            # 先解除区域和管理员账号的绑定，避免误删区域
            try:
                region = getattr(user, 'managed_region', None)
            except Exception:
                region = None

            if region:
                # 如果 Region 里有 admin_user 字段，则置空
                if hasattr(region, 'admin_user'):
                    region.admin_user = None
                    region.save()

            username = user.username
            user.delete()

        return APIResponse.success(
            message=f'区域管理员账号 {username} 删除成功'
        )

    except Exception as e:
        return APIResponse.error(
            message=f'删除失败：{str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )