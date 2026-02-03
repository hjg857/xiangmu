"""
评估系统视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Assessment, InstitutionAssessment, BehaviorAssessment, AssetAssessment, TechnologyAssessment
from .serializers import (
    AssessmentSerializer, InstitutionAssessmentSerializer,
    BehaviorAssessmentSerializer, AssetAssessmentSerializer, TechnologyAssessmentSerializer
)
from apps.regions.services import get_or_create_region_by_text
from apps.regions.utils.generators import gen_unique_school_username, gen_strong_password
from django.db import transaction
from apps.schools.models import School
import logging

from ..accounts.models import User

logger = logging.getLogger(__name__)


class AssessmentViewSet(viewsets.ModelViewSet):
    """评估记录视图集"""
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # 禁用分页

    # apps/assessments/views.py

    # apps/assessments/views.py
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """
        获取评估详细数据：绕过自动权限检查，直接使用 get_queryset 结果
        """
        try:
            # self.get_queryset() 会应用你之前写好的：if user.is_admin_user(): return Assessment.objects.all()
            assessment = self.get_queryset().get(pk=pk)
        except Assessment.DoesNotExist:
            return Response({"detail": "未找到评估记录或您没有权限访问"}, status=403)

        # 聚合数据逻辑（保持不变）
        institution, _ = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        behavior, _ = BehaviorAssessment.objects.get_or_create(assessment=assessment)
        asset, _ = AssetAssessment.objects.get_or_create(assessment=assessment)
        technology, _ = TechnologyAssessment.objects.get_or_create(assessment=assessment)

        return Response({
            'assessment': AssessmentSerializer(assessment).data,
            'institution': InstitutionAssessmentSerializer(institution).data,
            'behavior': BehaviorAssessmentSerializer(behavior).data,
            'asset': AssetAssessmentSerializer(asset).data,
            'technology': TechnologyAssessmentSerializer(technology).data,
            'scores': {
                'total_score': str(assessment.total_score),
                'maturity_level': assessment.maturity_level,
                'maturity_level_display': assessment.get_maturity_level_display(),
            }
        })


    def get_queryset(self):
        user = self.request.user

        # 针对 Swagger 等工具的保护及未登录拦截
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Assessment.objects.none()

        # 1. 超级管理员 (Admin)：拥有上帝视角，看全校数据
        if hasattr(user, 'is_admin_user') and user.is_admin_user():
            return Assessment.objects.all()

        # 2. 区域管理员 (Region Admin)：看自己管辖区域下的学校数据
        # 逻辑：Assessment -> School -> Region -> region_admin (当前用户)
        if hasattr(user, 'role') and user.role == 'region_admin':
            return Assessment.objects.filter(school__region__region_admin=user)

        # 3. 学校用户 (School)：只能看到自己学校的数据
        try:
            if hasattr(user, 'school'):
                return Assessment.objects.filter(school=user.school)
        except Exception:
            pass

        return Assessment.objects.none()

    def create(self, request, *args, **kwargs):
        """创建新评估 - 允许历史记录"""
        user = request.user
        school = user.school

        # 核心逻辑：检查是否【当前】有正在填写的评估
        # 只要状态不是 'completed'，就不允许开新的，必须把手头这份做完
        ongoing = Assessment.objects.filter(school=school).exclude(status='completed').first()

        if ongoing:
            if ongoing.status == 'draft':
                # 如果是草稿，直接返回旧的，让用户继续填
                serializer = self.get_serializer(ongoing)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': '当前已有评估正在处理中，请完成后再发起新评估'}, status=400)

        # 如果之前的都已完成（completed），则创建一份全新的记录
        assessment = Assessment.objects.create(school=school, status='draft')

        # 必须手动初始化子表，否则后面 save_xxx 会报错
        InstitutionAssessment.objects.create(assessment=assessment)
        BehaviorAssessment.objects.create(assessment=assessment)
        AssetAssessment.objects.create(assessment=assessment)
        TechnologyAssessment.objects.create(assessment=assessment)

        serializer = self.get_serializer(assessment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def admin_list(self, request):
        """管理员获取评估列表（带分页和筛选）"""
        if not request.user.is_admin_user():
            return Response(
                {'error': '只有管理员可以访问'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = Assessment.objects.all().order_by('-created_at')
        
        # 筛选
        school_name = request.query_params.get('school_name')
        status_param = request.query_params.get('status')
        
        if school_name:
            queryset = queryset.filter(school__name__icontains=school_name)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # 分页
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 20))
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def institution(self, request, pk=None):
        """获取数据制度评估数据"""
        try:
            assessment = self.get_queryset().get(pk=pk)  # 修改点
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        institution, created = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        serializer = InstitutionAssessmentSerializer(institution)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def save_institution(self, request, pk=None):
        """保存数据制度评估数据"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许修改
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法修改数据'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        institution, created = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        serializer = InstitutionAssessmentSerializer(institution, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='institution/upload')
    def upload_institution_file(self, request, pk=None):
        """上传数据制度文件"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许上传
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法上传文件'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        institution, created = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        
        file_type = request.data.get('file_type')  # 'management' or 'practice'
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            return Response({'error': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存文件
        from django.core.files.storage import default_storage
        file_path = f'institutions/{assessment.school.id}/{uploaded_file.name}'
        saved_path = default_storage.save(file_path, uploaded_file)
        
        # 获取URL（适配OSS）
        file_url = default_storage.url(saved_path)
        if not file_url.startswith('http'):
            file_url = request.build_absolute_uri(file_url)
        
        # 更新文件列表
        file_info = {
            'name': uploaded_file.name,
            'path': saved_path,
            'url': file_url,
            'size': uploaded_file.size,
            'uploaded_at': timezone.now().isoformat()
        }
        
        if file_type == 'management':
            files = institution.management_doc_files or []
            files.append(file_info)
            institution.management_doc_files = files
        elif file_type == 'practice':
            files = institution.practice_doc_files or []
            files.append(file_info)
            institution.practice_doc_files = files
        else:
            return Response({'error': '无效的文件类型'}, status=status.HTTP_400_BAD_REQUEST)
        
        institution.save()
        
        return Response({
            'message': '文件上传成功',
            'file': file_info
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='institution/delete-file')
    def delete_institution_file(self, request, pk=None):
        """删除数据制度文件"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许删除
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法删除文件'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        institution, created = InstitutionAssessment.objects.get_or_create(assessment=assessment)
        
        file_type = request.data.get('file_type')  # 'management' or 'practice'
        file_path = request.data.get('file_path')  # 要删除的文件路径
        
        if not file_path:
            return Response({'error': '未指定文件路径'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 从数据库中删除文件记录
            if file_type == 'management':
                files = institution.management_doc_files or []
                # 过滤掉要删除的文件
                updated_files = [f for f in files if f.get('path') != file_path]
                institution.management_doc_files = updated_files
            elif file_type == 'practice':
                files = institution.practice_doc_files or []
                updated_files = [f for f in files if f.get('path') != file_path]
                institution.practice_doc_files = updated_files
            else:
                return Response({'error': '无效的文件类型'}, status=status.HTTP_400_BAD_REQUEST)
            
            institution.save()
            
            # 尝试删除物理文件（可选，失败不影响数据库操作）
            try:
                from django.core.files.storage import default_storage
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                    logger.info(f"已删除物理文件: {file_path}")
            except Exception as e:
                logger.warning(f"删除物理文件失败: {str(e)}")
            
            return Response({
                'message': '文件删除成功',
                'file_path': file_path
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}", exc_info=True)
            return Response(
                {'error': f'删除文件失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def behavior(self, request, pk=None):
        """获取数据行为评估数据"""
        try:
            assessment = self.get_queryset().get(pk=pk)  # 修改点
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        behavior, created = BehaviorAssessment.objects.get_or_create(assessment=assessment)
        serializer = BehaviorAssessmentSerializer(behavior)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def save_behavior(self, request, pk=None):
        """保存数据行为评估数据"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许修改
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法修改数据'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        behavior, created = BehaviorAssessment.objects.get_or_create(assessment=assessment)
        serializer = BehaviorAssessmentSerializer(behavior, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def asset(self, request, pk=None):
        """获取数据资产评估数据"""
        try:
            assessment = self.get_queryset().get(pk=pk)  # 修改点
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        asset, created = AssetAssessment.objects.get_or_create(assessment=assessment)
        serializer = AssetAssessmentSerializer(asset)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def save_asset(self, request, pk=None):
        """保存数据资产评估数据"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许修改
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法修改数据'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        asset, created = AssetAssessment.objects.get_or_create(assessment=assessment)
        serializer = AssetAssessmentSerializer(asset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def technology(self, request, pk=None):
        """获取数据技术评估数据"""
        try:
            assessment = self.get_queryset().get(pk=pk)  # 修改点
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        technology, created = TechnologyAssessment.objects.get_or_create(assessment=assessment)
        serializer = TechnologyAssessmentSerializer(technology)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def save_technology(self, request, pk=None):
        """保存数据技术评估数据"""
        assessment = self.get_object()
        
        # 检查评估状态，只有草稿状态才允许修改
        if assessment.status != 'draft':
            return Response(
                {'error': '评估已提交，无法修改数据'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        technology, created = TechnologyAssessment.objects.get_or_create(assessment=assessment)
        serializer = TechnologyAssessmentSerializer(technology, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        提交评估，触发计分任务
        """
        assessment = self.get_object()
        
        # 检查评估状态
        if assessment.status == 'completed':
            return Response(
                {'error': '评估已完成，无法重复提交'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否有必要的数据
        # TODO: 添加数据完整性检查
        
        # 更新状态为数据收集完成
        assessment.status = 'collecting'
        assessment.save()
        
        # 触发异步计分任务
        from .tasks import calculate_assessment_scores
        task = calculate_assessment_scores.delay(assessment.id)
        
        logger.info(f"评估 {assessment.id} 已提交，任务ID: {task.id}")
        
        return Response({
            'message': '评估已提交，正在计算中',
            'task_id': task.id,
            'assessment_id': assessment.id
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def scores(self, request, pk=None):
        """
        获取评估得分详情
        """
        try:
            assessment = self.get_queryset().get(pk=pk)
        except Assessment.DoesNotExist:
            return Response({'error': '无权访问'}, status=403)
        
        if assessment.status != 'completed':
            return Response({
                'status': assessment.status,
                'message': '评估尚未完成'
            })
        
        return Response({
            'status': 'completed',
            'scores': {
                'literacy_score': str(assessment.literacy_score),
                'institution_score': str(assessment.institution_score),
                'behavior_score': str(assessment.behavior_score),
                'asset_score': str(assessment.asset_score),
                'technology_score': str(assessment.technology_score),
                'total_score': str(assessment.total_score),
                'maturity_level': assessment.maturity_level,
                'maturity_level_display': assessment.get_maturity_level_display()
            },
            'completed_at': assessment.completed_at
        })
