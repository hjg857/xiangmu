from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.assessments.models import Assessment
from apps.assessments.serializers import RegionAssessmentListSerializer

from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated

from apps.assessments.models import Assessment
from apps.regions.pagination import StandardPagePagination
from .permissions import IsRegionAdmin
from .serializers_region_admin import RegionAssessmentListItemSerializer

from apps.assessments.serializers import (
    InstitutionAssessmentSerializer,
    BehaviorAssessmentSerializer,
    AssetAssessmentSerializer,
    TechnologyAssessmentSerializer,
)


class RegionAssessmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 必须是区域管理员
        if user.role != 'region_admin':
            return Response(
                {'success': False, 'message': '无权限访问'},
                status=403
            )

        # 必须绑定区县
        region = getattr(user, 'managed_region', None)
        if not region:
            return Response(
                {'success': False, 'message': '未绑定区域'},
                status=400
            )

        # 查询该区县下的评估
        assessments = Assessment.objects.filter(
            school__region=region
        ).select_related('school').order_by('-created_at')

        serializer = RegionAssessmentListSerializer(assessments, many=True)

        return Response({
            'success': True,
            'message': 'success',
            'data': {
                'region': {
                    'id': region.id,
                    'name': region.name,
                    'province': region.province,
                    'city': region.city,
                },
                'assessments': serializer.data
            }
        })

class RegionAssessmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        user = request.user

        # 必须是区域管理员
        if user.role != 'region_admin':
            return Response(
                {'success': False, 'message': '无权限访问'},
                status=403
            )

        # 必须绑定区域
        region = getattr(user, 'managed_region', None)
        if not region:
            return Response(
                {'success': False, 'message': '未绑定区域'},
                status=400
            )

        # 获取评估
        assessment = get_object_or_404(
            Assessment.objects.select_related('school'),
            id=assessment_id
        )

        # 校验评估是否属于该区域
        if assessment.school.region_id != region.id:
            return Response(
                {'success': False, 'message': '无权限访问该评估'},
                status=403
            )

        # 组装返回数据（只读）
        data = {
            'assessment': {
                'id': assessment.id,
                'school': {
                    'id': assessment.school.id,
                    'name': assessment.school.name
                },
                'status': assessment.status,
                'total_score': assessment.total_score,
                'maturity_level': assessment.maturity_level,
                'completed_at': assessment.completed_at,
            },
            'institution': InstitutionAssessmentSerializer(
                getattr(assessment, 'institution', None)
            ).data if hasattr(assessment, 'institution') else None,
            'behavior': BehaviorAssessmentSerializer(
                getattr(assessment, 'behavior', None)
            ).data if hasattr(assessment, 'behavior') else None,
            'asset': AssetAssessmentSerializer(
                getattr(assessment, 'asset', None)
            ).data if hasattr(assessment, 'asset') else None,
            'technology': TechnologyAssessmentSerializer(
                getattr(assessment, 'technology', None)
            ).data if hasattr(assessment, 'technology') else None,
        }

        return Response({
            'success': True,
            'message': 'success',
            'data': data
        })


def api_ok(data=None, message="success"):
    return Response({"success": True, "message": message, "data": data or {}})


def api_fail(message="error", http_code=http_status.HTTP_400_BAD_REQUEST):
    return Response({"success": False, "message": message}, status=http_code)


class RegionAdminAssessmentListView(APIView):
    permission_classes = [IsAuthenticated, IsRegionAdmin]

    def get(self, request):
        region = request.user.managed_region

        qs = (
            Assessment.objects
            .select_related("school", "school__region")
            .filter(school__region=region)
        )

        # ---- filters ----
        status_v = request.query_params.get("status")
        if status_v:
            qs = qs.filter(status=status_v)

        maturity = request.query_params.get("maturity_level")
        if maturity:
            qs = qs.filter(maturity_level=maturity)

        school_name = request.query_params.get("school_name")
        if school_name:
            qs = qs.filter(school__name__icontains=school_name)

        has_report = request.query_params.get("has_report")
        if has_report in ("true", "false"):
            if has_report == "true":
                qs = qs.exclude(report_file="").exclude(report_file__isnull=True)
            else:
                qs = qs.filter(Q(report_file="") | Q(report_file__isnull=True))

        # ---- ordering ----
        ordering = request.query_params.get("ordering") or "-completed_at,-created_at"
        allowed = {
            "completed_at", "-completed_at",
            "created_at", "-created_at",
            "total_score", "-total_score",
            "school__name", "-school__name",
        }
        order_fields = [f.strip() for f in ordering.split(",") if f.strip() in allowed]
        if order_fields:
            qs = qs.order_by(*order_fields)

        # ---- summary（基于过滤前 or 过滤后？建议：过滤后更符合页面）----
        # 这里用过滤后的 qs 统计：更符合“当前筛选结果”
        summary = qs.aggregate(
            school_count=Count("school", distinct=True),
            has_assessment_count=Count("id"),
            completed_count=Count("id", filter=Q(status="completed")),
            report_count=Count("id", filter=~Q(report_file="") & Q(report_file__isnull=False)),
        )

        # ---- paginate ----
        paginator = StandardPagePagination()
        page_qs = paginator.paginate_queryset(qs, request, view=self)

        serializer = RegionAssessmentListItemSerializer(
            page_qs, many=True, context={"request": request}
        )

        data = {
            "region": {
                "id": region.id,
                "code": region.code,
                "province": region.province,
                "city": region.city,
                "name": region.name,
            },
            "summary": summary,
            "assessments": serializer.data,
            "pagination": {
                "page": paginator.page.number,
                "page_size": paginator.get_page_size(request),
                "total": paginator.page.paginator.count,
                "total_pages": paginator.page.paginator.num_pages,
            },
        }
        return api_ok(data)

