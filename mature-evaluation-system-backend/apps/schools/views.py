"""
学校模块视图
"""
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404

from django.db import transaction
from rest_framework.response import Response

from config import settings
from .models import School, AccountApplication
from .serializers import (
    SchoolSerializer, AccountApplicationSerializer,
    AccountApplicationCreateSerializer, SchoolAdminSerializer
)
from utils.response import APIResponse
from utils.generators import generate_username, generate_strong_password
from apps.accounts.models import User
from .tasks import send_account_approval_email
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from apps.regions.utils.generators import gen_unique_school_username, gen_strong_password
from apps.regions.services import get_or_create_region_by_text
from ..regions.models import Region


@api_view(['POST'])
@permission_classes([AllowAny])
def create_application(request):
    """提交账号申请"""
    # 打印接收到的数据用于调试
    print("接收到的申请数据:", request.data)
    
    serializer = AccountApplicationCreateSerializer(data=request.data)

    if not serializer.is_valid():
        print("验证失败:", serializer.errors)

        first_error = None
        for field, errors in serializer.errors.items():
            if isinstance(errors, list) and errors:
                first_error = errors[0]
                break

        return APIResponse.error(
            message=first_error or '提交失败，请检查表单',
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    application = serializer.save()
    
    # 记录操作日志
    from apps.admin_panel.models import OperationLog
    OperationLog.objects.create(
        user=None,
        operation_type='application_submit',
        operation_desc=f'提交账号申请：{application.school_name}',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return APIResponse.success(
        data=AccountApplicationSerializer(application).data,
        message='申请提交成功，请等待审批',
        status_code=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_application_status(request, application_id):
    """查询申请状态"""
    application = get_object_or_404(AccountApplication, id=application_id)
    
    return APIResponse.success(
        data=AccountApplicationSerializer(application).data
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_applications(request):
    """获取申请列表（管理员）"""
    print(f"用户: {request.user.username}, 角色: {request.user.role}")

    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以访问',
            status_code=status.HTTP_403_FORBIDDEN
        )

    # 获取查询参数
    status_filter = request.query_params.get('status', None)
    school_type_filter = request.query_params.get('school_type', None)
    apply_role_filter = request.query_params.get('apply_role', None)
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)

    # 构建查询：默认显示所有申请，包括学校用户和区域管理员
    queryset = AccountApplication.objects.all().order_by('-applied_at')
    print(f"总申请数: {queryset.count()}")

    # 按申请角色筛选：school / region_admin
    if apply_role_filter and apply_role_filter not in ['all', 'undefined', 'null', '']:
        queryset = queryset.filter(apply_role=apply_role_filter)
        print(f"按申请角色筛选后: {queryset.count()}")

    # 按状态筛选
    if status_filter and status_filter not in ['all', 'undefined', 'null', '']:
        queryset = queryset.filter(status=status_filter)
        print(f"按状态筛选后: {queryset.count()}")

    # 按学校类型筛选
    # 注意：region_admin 不是学校类型，而是申请角色
    if school_type_filter and school_type_filter not in ['all', 'undefined', 'null', '']:
        if school_type_filter == 'region_admin':
            queryset = queryset.filter(apply_role='region_admin')
        else:
            queryset = queryset.filter(apply_role='school', school_type=school_type_filter)

        print(f"按学校类型/角色筛选后: {queryset.count()}")

    # 按时间范围筛选
    if start_date:
        from datetime import datetime
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        queryset = queryset.filter(applied_at__gte=start_datetime)
        print(f"按开始时间筛选后: {queryset.count()}")

    if end_date:
        from datetime import datetime, timedelta
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        queryset = queryset.filter(applied_at__lt=end_datetime)
        print(f"按结束时间筛选后: {queryset.count()}")

    # 分页
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = int(request.query_params.get('page_size', 20))
    page = paginator.paginate_queryset(queryset, request)

    if page is not None:
        serializer = AccountApplicationSerializer(page, many=True)
        print(f"返回数据: {len(serializer.data)} 条")
        return paginator.get_paginated_response(serializer.data)

    serializer = AccountApplicationSerializer(queryset, many=True)
    return APIResponse.success(data=serializer.data)


from django.core.paginator import Paginator
from django.utils import timezone

from apps.schools.models import School
from apps.regions.models import Region
from apps.accounts.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_schools(request):
    """获取区校账户列表（管理员）：学校账号 + 区域管理员账号"""
    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以访问',
            status_code=status.HTTP_403_FORBIDDEN
        )

    # 获取查询参数
    name = request.query_params.get('name', None)
    account_type = request.query_params.get('account_type', None)
    school_type = request.query_params.get('school_type', None)
    province = request.query_params.get('province', None)
    city = request.query_params.get('city', None)

    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))

    result_rows = []

    # =========================
    # 1. 学校账号
    # =========================
    if account_type in [None, '', 'school']:
        school_qs = School.objects.all().order_by('-created_at')

        if name:
            school_qs = school_qs.filter(name__icontains=name)

        if school_type:
            school_qs = school_qs.filter(school_type=school_type)

        if province:
            school_qs = school_qs.filter(province=province)

        if city:
            school_qs = school_qs.filter(city=city)

        school_data = SchoolAdminSerializer(school_qs, many=True).data

        # 给原学校数据补统一字段
        school_map = {school.id: school for school in school_qs}

        for item in school_data:
            school_id = item.get('id')
            school_obj = school_map.get(school_id)

            user = getattr(school_obj, 'user', None) if school_obj else None

            item['account_type'] = 'school'
            item['username'] = getattr(user, 'username', '') if user else ''
            item['school_name'] = item.get('name') or ''
            item['display_name'] = item.get('name') or ''
            item['region_name'] = ''

            # 用于统一排序，返回前删除
            item['_sort_time'] = school_obj.created_at if school_obj else None

            result_rows.append(item)

    # =========================
    # 2. 区域管理员账号
    # =========================
    # =========================
    # 2. 区域管理员账号
    # =========================
    if account_type in [None, '', 'region_admin']:
        region_admin_qs = User.objects.filter(role='region_admin').order_by('-created_at')

        for user in region_admin_qs:
            # 优先从 user.managed_region 获取区域
            try:
                region = getattr(user, 'managed_region', None)
            except Exception:
                region = None

            # 兼容 user.region
            if not region:
                try:
                    region = getattr(user, 'region', None)
                except Exception:
                    region = None

            # 兼容 Region.admin_user
            if not region:
                try:
                    region = Region.objects.filter(admin_user=user).first()
                except Exception:
                    region = None

            region_province = getattr(region, 'province', '') if region else ''
            region_city = getattr(region, 'city', '') if region else ''
            region_district = getattr(region, 'name', '') if region else ''

            if name:
                name_text = (
                    f'{region_province}{region_city}{region_district}'
                    f'{user.username or ""}'
                    f'{user.email or ""}'
                )
                if name not in name_text:
                    continue

            if province and region_province != province:
                continue

            if city and region_city != city:
                continue

            if school_type and school_type != 'region_admin':
                continue

            application = AccountApplication.objects.filter(
                apply_role='region_admin',
                province=region_province,
                city=region_city,
                district=region_district
            ).order_by('-applied_at').first()

            contact_name = (
                    getattr(region, 'contact_name', '') or
                    (application.contact_name if application else '') or
                    ''
            )

            contact_phone = (
                    getattr(region, 'contact_phone', '') or
                    (application.contact_phone if application else '') or
                    ''
            )

            contact_email = (
                    getattr(region, 'contact_email', '') or
                    (application.contact_email if application else '') or
                    user.email or
                    ''
            )

            region_name = (
                f'{region_city}{region_district}区域管理'
                if (region_city or region_district)
                else '区域管理'
            )

            result_rows.append({
                'id': user.id,
                'account_type': 'region_admin',
                'name': region_name,
                'school_name': region_name,
                'display_name': region_name,
                'school_type': 'region_admin',
                'school_type_display': '区域管理',

                'province': region_province,
                'city': region_city,
                'district': region_district,
                'region_id': getattr(region, 'id', None) if region else None,
                'region_name': region_name,

                'contact_name': contact_name,
                'contact_phone': contact_phone,
                'contact_email': contact_email,

                'username': user.username,
                'created_at': user.created_at,
                'latest_assessment': None,

                '_sort_time': user.created_at,
            })

    # =========================
    # 3. 统一排序
    # =========================
    result_rows.sort(
        key=lambda x: x.get('_sort_time') or timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )

    for item in result_rows:
        item.pop('_sort_time', None)

    # =========================
    # 4. 手动分页
    # =========================
    paginator = Paginator(result_rows, page_size)
    page_obj = paginator.get_page(page)

    return Response({
        'count': paginator.count,
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'results': list(page_obj.object_list)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_school_info(request):
    """获取当前学校信息"""
    if (not request.user.is_school_user()) and not request.user.is_admin():
        return APIResponse.error(
            message='只有学校用户可以访问',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    try:
        school = request.user.school
        return APIResponse.success(SchoolSerializer(school).data)
    except School.DoesNotExist:
        return APIResponse.error(
            message='学校信息不存在',
            status_code=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_school_info(request):
    """更新学校信息"""
    if not request.user.is_school_user():
        return APIResponse.error(
            message='只有学校用户可以访问',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    try:
        school = request.user.school
    except School.DoesNotExist:
        return APIResponse.error(
            message='学校信息不存在',
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    serializer = SchoolSerializer(school, data=request.data, partial=True)
    
    if not serializer.is_valid():
        return APIResponse.error(
            message='更新失败',
            details=serializer.errors
        )
    
    serializer.save()
    
    # 记录操作日志
    from apps.admin_panel.models import OperationLog
    OperationLog.objects.create(
        user=request.user,
        operation_type='school_update',
        operation_desc='更新学校信息',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return APIResponse.success(
        data=serializer.data,
        message='更新成功'
    )


@api_view(['POST', 'PATCH'])  # 建议支持 PATCH
@permission_classes([IsAuthenticated])
def update_school_info_count(request):
    try:
        # 获取当前登录用户的学校对象
        school = request.user.school

        # 从请求中获取数据
        school.student_count = request.data.get('student_count', school.student_count)
        school.teacher_count = request.data.get('teacher_count', school.teacher_count)
        school.founding_year = request.data.get('founding_year', school.founding_year)

        school.save()
        return Response({"success": True, "message": "学校信息更新成功"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_application(request, application_id):
    """审批账号申请（管理员）"""
    if not request.user.is_admin_user():
        return APIResponse.error(message='只有管理员可以审批', status_code=status.HTTP_403_FORBIDDEN)

    application = get_object_or_404(AccountApplication, id=application_id)
    if application.status != 'pending':
        return APIResponse.error('该申请已处理')

    if User.objects.filter(email=application.contact_email).exists():
        return APIResponse.error('该邮箱已被注册，请联系管理员')

    try:
        with transaction.atomic():
            # 1. 生成凭证
            username = gen_unique_school_username(application.school_name, User)
            password = gen_strong_password(8)
            # 修正：去掉逗号，防止变成元组
            access_code = password

            # 2. 确定角色
            # 这里的角色直接决定了登录后的权限：'school' 或 'region_admin'
            target_role = getattr(application, 'apply_role', 'school')

            # 3. 创建用户
            user = User.objects.create_user(
                username=username,
                email=application.contact_email,
                password=password,
                role=target_role # 核心：赋予对应的系统角色
            )

            # 4. 根据角色处理关联数据
            region = None
            if hasattr(application, 'district_code') and application.district_code:
                region = Region.objects.filter(code=application.district_code).first()

            if not region:
                region = get_or_create_region_by_text(
                    application.province, application.city, application.district, application.district_code
                )

            if target_role == 'school':
                # 如果是学校申请，创建学校档案
                School.objects.create(
                    user=user,
                    name=application.school_name,
                    school_type=application.school_type,
                    province=application.province,
                    city=application.city,
                    district=application.district,
                    region=region,
                    contact_name=application.contact_name,
                    contact_position=application.contact_position,
                    contact_phone=application.contact_phone,
                    contact_email=application.contact_email,
                    access_code=access_code
                )
            elif target_role == 'region_admin':
                # 如果是区域管理员申请，通常将其与 Region 记录绑定
                # 假设你的 Region 模型有一个 region_admin 字段指向 User
                if region:
                    region.region_admin = user
                    region.save(update_fields=['region_admin'])

                # 可选：如果区域管理员也需要一个“虚拟学校”外壳，可以在此处也创建 School
                # 但通常 region_admin 角色登录后直接看全区数据，不需要 School 记录

            # 5. 更新申请状态
            application.status = 'approved'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            # 发送邮件（同步方式，避免Celery配置问题）
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                subject = '【中小学数据文化成熟度评估监测系统】账号审批通过通知'
                message = f"""尊敬的 {application.school_name} 用户：

您好！

您的账号申请已通过审核，以下是您的登录信息：

登录地址：{settings.FRONTEND_URL}
用户名：{username}
密码：{password}

祝 工作顺利，万事如意！

苏师YangTeam

此邮件由系统自动发送，请勿回复

======================================================

温馨提示：

1、请妥善保管您的账号信息
2、建议首次登录后及时修改密码
3、如有任何问题，请联系管理员

联系人：曾老师
电  话：18252169610
邮  件：2020250606@jsnu.edu.cn
邮  编：221116
地  址：江苏省徐州市铜山新区上海路101号

======================================================"""
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[application.contact_email],
                    fail_silently=True,  # 邮件发送失败不影响审批
                )
            except Exception as e:
                print(f'邮件发送失败: {str(e)}')
            
            # 记录操作日志
            from apps.admin_panel.models import OperationLog
            OperationLog.objects.create(
                user=request.user,
                operation_type='application_approve',
                operation_desc=f'审批通过账号申请：{application.school_name}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            return APIResponse.success(
                data={'username': username, 'role': target_role},
                message='审批成功，账号信息已发送'
            )
            
    except Exception as e:
        return APIResponse.error(
            message=f'审批失败：{str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_application(request, application_id):
    """拒绝账号申请（管理员）"""
    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以审批',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    application = get_object_or_404(AccountApplication, id=application_id)
    
    if application.status != 'pending':
        return APIResponse.error('该申请已处理')
    
    reject_reason = request.data.get('reject_reason', '')
    
    if not reject_reason:
        return APIResponse.error('请填写拒绝原因')
    
    # 更新申请状态
    from django.utils import timezone
    application.status = 'rejected'
    application.reject_reason = reject_reason
    application.reviewed_by = request.user
    application.reviewed_at = timezone.now()
    application.save()
    
    # 发送拒绝通知邮件
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = '【中小学数据文化成熟度评估监测系统】账号申请审核结果通知'
        message = f"""
尊敬的 {application.school_name} 用户：

您好！

很遗憾地通知您，您的账号申请未能通过审核。

拒绝原因：
{reject_reason}

如有疑问，请联系管理员。

---
智能学习与评价江苏省产业技术工程化中心
邮箱:2020250606@jsnu.edu.cn
地址:江苏省徐州市铜山新区上海路101号
{settings.SYSTEM_EMAIL_SIGNATURE}
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER or 'noreply@example.com',
            recipient_list=[application.contact_email],
            fail_silently=True,  # 邮件发送失败不影响拒绝操作
        )
        print(f'拒绝通知邮件已发送至: {application.contact_email}')
    except Exception as e:
        print(f'邮件发送失败: {str(e)}')
    
    # 记录操作日志
    from apps.admin_panel.models import OperationLog
    OperationLog.objects.create(
        user=request.user,
        operation_type='application_reject',
        operation_desc=f'拒绝账号申请：{application.school_name}',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return APIResponse.success(message='已拒绝申请，通知邮件已发送')



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_school(request, school_id):
    """删除学校（管理员）- 级联删除所有关联数据"""
    if not request.user.is_admin_user():
        return APIResponse.error(
            message='只有管理员可以删除学校',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    school = get_object_or_404(School, id=school_id)
    school_name = school.name
    user = school.user  # 保存 user 引用
    
    try:
        with transaction.atomic():
            # 1. 删除 School（会自动级联删除所有 Assessment 及子模块）
            school.delete()
            
            # 2. 删除关联的 User
            user.delete()
            
            # 3. 删除对应的账号申请记录（按学校名称匹配）
            deleted_apps = AccountApplication.objects.filter(school_name=school_name).delete()
            
            # 记录操作日志
            from apps.admin_panel.models import OperationLog
            OperationLog.objects.create(
                user=request.user,
                operation_type='school_delete',
                operation_desc=f'删除学校：{school_name}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return APIResponse.success(
                message=f'已删除学校"{school_name}"及其所有关联数据'
            )
    except Exception as e:
        return APIResponse.error(
            message=f'删除失败：{str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def check_application_by_email(request):
    """通过邮箱查询申请状态"""
    email = request.data.get('email')
    
    if not email:
        return APIResponse.error('请提供邮箱地址')
    
    try:
        # 查找最新的申请记录
        application = AccountApplication.objects.filter(
            contact_email=email
        ).order_by('-applied_at').first()
        
        if not application:
            return APIResponse.error(
                message='未找到该邮箱的申请记录',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return APIResponse.success(
            data=AccountApplicationSerializer(application).data
        )
    except Exception as e:
        return APIResponse.error(
            message='查询失败',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
def send_contact_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            subject = f"合作咨询 - 中小学校数据文化成熟度评估"
            message = f"""
联系人：{data['name']}
联系电话：{data['phone']}
联系邮箱：{data['email']}
合作意向：{data['type']}

留言内容：
{data['message']}
            """
            from_email = data['email']  # 默认发件邮箱
            recipient_list = ["hjg151318@163.com"]  # 收件人邮箱

            send_mail(subject, message, from_email, recipient_list)
            return JsonResponse({"success": True, "message": "邮件发送成功"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "请求方法错误"})

import re
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_schools(request):
    """超级管理员批量导入学校账号"""
    if not request.user.is_admin_user():
        return Response(
            {'success': False, 'message': '只有超级管理员可以操作'},
            status=403
        )

    rows = request.data.get('rows', [])

    if not isinstance(rows, list) or not rows:
        return Response(
            {'success': False, 'message': '数据为空'},
            status=400
        )

    if len(rows) > 100:
        rows = rows[:100]

    report = {
        'total': len(rows),
        'created': 0,
        'skipped': 0,
        'failed': 0,
        'details': []
    }

    seen_name = set()
    seen_email = set()
    seen_username = set()

    valid_school_types = {
        'primary',
        'junior',
        'senior',
        'nine_year',
        'twelve_year'
    }

    for idx, row in enumerate(rows):
        try:
            name = (row.get('school_name') or row.get('name') or '').strip()
            school_type = (row.get('school_type') or '').strip()

            province = (row.get('province') or '').strip()
            city = (row.get('city') or '').strip()
            district = (row.get('district') or '').strip()

            contact_name = (row.get('contact_name') or '').strip()
            contact_position = (row.get('contact_position') or '').strip()
            contact_phone = (row.get('contact_phone') or '').strip()
            contact_email = (row.get('contact_email') or '').strip()

            username = (row.get('username') or '').strip()
            password = (row.get('password') or '').strip()

            # 1. 必填校验
            missing_fields = []

            if not name:
                missing_fields.append('学校名称')
            if not school_type:
                missing_fields.append('学校类型')
            if not province:
                missing_fields.append('省')
            if not city:
                missing_fields.append('市')
            if not district:
                missing_fields.append('区/县')
            if not contact_name:
                missing_fields.append('负责人')
            if not contact_position:
                missing_fields.append('职务')
            if not contact_phone:
                missing_fields.append('联系电话')
            if not contact_email:
                missing_fields.append('邮箱')
            if not username:
                missing_fields.append('登录用户名')
            if not password:
                missing_fields.append('登录密码')

            if missing_fields:
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': f"必填项缺失：{'、'.join(missing_fields)}"
                })
                continue

            # 2. 字段格式校验
            if school_type not in valid_school_types:
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': '学校类型不合法'
                })
                continue

            if not re.fullmatch(r'1[3-9]\d{9}', contact_phone):
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': '联系电话格式不正确，请填写11位手机号'
                })
                continue

            if not re.fullmatch(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', contact_email):
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': '邮箱格式不正确'
                })
                continue

            if not re.fullmatch(r'[A-Za-z0-9]+', username):
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': '登录用户名只能包含数字或字母，不能包含特殊字符'
                })
                continue

            if not re.fullmatch(r'[A-Za-z0-9]{8}', password):
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': '登录密码必须为8位数字或字母组合'
                })
                continue

            # 3. 文件内重复校验
            norm_name = re.sub(r'\s+', '', name).lower()
            norm_email = contact_email.lower()
            norm_username = username.lower()

            if norm_name in seen_name:
                report['skipped'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'skipped',
                    'reason': '文件内学校名称重复，已跳过'
                })
                continue
            seen_name.add(norm_name)

            if norm_email in seen_email:
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': '文件内邮箱重复'
                })
                continue
            seen_email.add(norm_email)

            if norm_username in seen_username:
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': '文件内登录用户名重复'
                })
                continue
            seen_username.add(norm_username)

            # 4. 数据库唯一性校验
            if User.objects.filter(email=contact_email).exists():
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': '该邮箱已被注册'
                })
                continue

            if User.objects.filter(username=username).exists():
                report['failed'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'failed',
                    'reason': '登录用户名已存在，请更换用户名'
                })
                continue

            # 5. 创建或获取区域
            region = get_or_create_region_by_text(
                province=province,
                city=city,
                district=district
            )

            # 同一区域下学校重名则跳过
            if School.objects.filter(region=region, name=name).exists():
                report['skipped'] += 1
                report['details'].append({
                    'row_index': idx,
                    'status': 'skipped',
                    'reason': '同一区域下已存在同名学校，已跳过'
                })
                continue

            # 6. 创建账号和学校
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=contact_email,
                    role='school',
                    is_active=True,
                    is_staff=False
                )

                # 如果 User 模型有锁定字段，可以保留
                if hasattr(user, 'is_locked'):
                    user.is_locked = False
                if hasattr(user, 'locked_until'):
                    user.locked_until = None
                user.save()

                school = School.objects.create(
                    user=user,
                    name=name,
                    school_type=school_type,
                    province=province,
                    city=city,
                    district=district,
                    region=region,
                    contact_name=contact_name,
                    contact_position=contact_position,
                    contact_phone=contact_phone,
                    contact_email=contact_email,
                    access_code=password
                )

            # 7. 发送邮件，失败不影响导入结果
            subject = '【中小学数据文化成熟度评估监测系统】账号审批通过通知'
            message = f"""尊敬的 {name} 用户：

您好！

您的账号申请已通过审核，以下是您的登录信息：

登录地址：{settings.FRONTEND_URL}
用户名：{username}
密码：{password}

祝 工作顺利，万事如意！

苏师YangTeam

此邮件由系统自动发送，请勿回复

======================================================

温馨提示：

1、请妥善保管您的账号信息
2、建议首次登录后及时修改密码
3、如有任何问题，请联系管理员

联系人：曾老师
电  话：18252169610
邮  件：2020250606@jsnu.edu.cn
邮  编：221116
地  址：江苏省徐州市铜山新区上海路101号

======================================================"""

            email_sent = False
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [contact_email],
                    fail_silently=True
                )
                email_sent = True
            except Exception:
                email_sent = False

            report['created'] += 1
            report['details'].append({
                'row_index': idx,
                'status': 'created',
                'school_id': school.id,
                'username': username,
                'password': password,
                'email_sent': email_sent
            })

        except Exception as e:
            report['failed'] += 1
            report['details'].append({
                'row_index': idx,
                'status': 'failed',
                'reason': str(e)
            })

    return Response({
        'success': True,
        'data': report
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_collaboration(request):
    name = request.data.get('name')
    phone = request.data.get('phone')
    email = request.data.get('email')
    intent_type = request.data.get('type')
    message = request.data.get('message')

    # 构造发送给团队的邮件内容
    subject = f"【合作咨询】来自：{name}"
    body = f"""
    收到新的合作咨询申请：

    联系人：{name}
    联系电话：{phone}
    联系邮箱：{email}
    合作意向：{intent_type}

    留言内容：
    {message}
    """

    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            ['2020250606@jsnu.edu.cn'],  # 接收人
            fail_silently=False,
        )
        return Response({"success": True, "message": "提交成功，我们会尽快联系您"})
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_accounts(request):
    """
    超级管理员专用：全量导出学校账号数据
    接口路径：GET /api/schools/export-accounts/
    """
    # 1. 权限拦截
    if not request.user.is_admin_user():
        return Response({'success': False, 'message': '权限不足'}, status=403)

    # 2. 获取数据 (select_related 减少 SQL 查询)
    schools = School.objects.all().select_related('user').order_by('-created_at')

    # 3. 组织数据格式
    data_list = []
    for s in schools:
        data_list.append({
            "school_name": s.name,
            "username": s.user.username if s.user else "未配置",
            "access_code": s.access_code or "未记录",
            "contact_name": s.contact_name,
            "contact_phone": s.contact_phone
        })

    return Response({
        "success": True,
        "data": data_list
    })