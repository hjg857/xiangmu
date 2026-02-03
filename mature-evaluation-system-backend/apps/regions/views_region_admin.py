import datetime
import hashlib

from django.db.models import OuterRef, Subquery, Exists, Count, Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status, status
from rest_framework.permissions import IsAuthenticated

from openpyxl import Workbook
import io
import re

from apps.accounts.permissions import IsRegionAdmin, get_user_region
from apps.accounts.models import User
from apps.schools.models import School, AccountApplication
from apps.assessments.models import Assessment
from apps.regions.models import Region
from apps.regions.pagination import StandardPagePagination

from .serializers_region_admin import (
    RegionAssessmentListItemSerializer,
    RegionAdminAssessmentListSerializer,
    RegionAdminAssessmentDetailSerializer,
    RegionAdminSchoolImportRowSerializer,
)
from .serializers_create_school import RegionAdminCreateSchoolSerializer

from utils.response import APIResponse
from .email_utils import send_school_account_email

from .utils.generators import USERNAME_RE, gen_unique_school_username, gen_strong_password


def ok(data=None, message="success"):
    return Response({"success": True, "message": message, "data": data})


def bad(message="bad request", code=http_status.HTTP_400_BAD_REQUEST):
    return Response({"success": False, "message": message}, status=code)


def try_send_account_email(*, school_name: str, to_email: str, username: str, password: str, log_prefix: str):
    """
    邮件发送失败不影响主流程：返回 True/False
    """
    try:
        sent = send_school_account_email(
            school_name=school_name,
            to_email=to_email,
            username=username,
            password=password,
        )
        if not sent:
            print(f"[{log_prefix}] 邮件发送失败: to={to_email}, school={school_name}")
        return bool(sent)
    except Exception as e:
        print(f"[{log_prefix}] 邮件发送异常: to={to_email}, school={school_name}, err={e}")
        return False


class RegionAdminBaseAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRegionAdmin]

    def get_region(self, request) -> Region:
        region = get_user_region(request.user)
        if not region:
            raise ValueError("当前区域管理员未绑定区县 Region")
        if not region.is_active:
            raise ValueError("当前区县 Region 未启用")
        return region

    def get_region_schools_qs(self, request):
        region = self.get_region(request)
        return School.objects.filter(region=region)


class RegionAdminOverviewView(RegionAdminBaseAPIView):
    """
    GET /api/region-admin/overview/
    """
    def get(self, request):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

        schools_qs = School.objects.filter(region=region)

        # 是否存在评估
        has_assessment = Exists(Assessment.objects.filter(school_id=OuterRef("pk")))

        school_count = schools_qs.count()
        has_assessment_count = schools_qs.annotate(has_assessment=has_assessment).filter(has_assessment=True).count()

        # 完成数：status == completed
        completed_count = Assessment.objects.filter(school__region=region, status="completed").count()

        # 有报告文件数：report_file 非空（FileField空字符串表示未上传/生成）
        report_count = Assessment.objects.filter(
            school__region=region
        ).exclude(report_file="").count()

        data = {
            "region": {
                "id": region.id,
                "code": region.code,
                "name": region.name,
                "province": region.province,
                "city": region.city,
                "level": region.level,
            },
            "school_count": school_count,
            "has_assessment_count": has_assessment_count,
            "completed_count": completed_count,
            "report_count": report_count,
        }
        return ok(data)


class RegionAdminSchoolListView(RegionAdminBaseAPIView):
    """
    GET /api/region-admin/schools/
     返回：已通过 School + 申请 AccountApplication(pending/rejected)
    支持：
      ?q=关键字（学校名/ID/账号）
      ?apply_status=pending/approved/rejected
      ?school_type=primary/junior/...
      ?page, page_size
    """
    def get(self, request):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

        q = (request.query_params.get("q") or "").strip()
        apply_status = (request.query_params.get("apply_status") or "").strip()
        school_type = (request.query_params.get("school_type") or "").strip()



        page = int(request.query_params.get("page", 1) or 1)
        page_size = int(request.query_params.get("page_size", 10) or 10)
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        start_at_str = request.query_params.get("start_at")
        end_at_str = request.query_params.get("end_at")
        start_dt = None
        if start_at_str:
            sd = parse_date(start_at_str)
            if sd:
                start_dt = datetime.datetime.combine(sd, datetime.time.min)

        end_dt = None
        if end_at_str:
            ed = parse_date(end_at_str)
            if ed:
                end_dt = datetime.datetime.combine(ed, datetime.time.max)
        # ============ 1) 已通过：School ============
        schools_qs = School.objects.filter(region=region).select_related("user").order_by("-created_at")

        if school_type:
            schools_qs = schools_qs.filter(school_type=school_type)

        if q:
            # q 支持：name / id / username
            schools_qs = schools_qs.filter(
                Q(name__icontains=q) |
                Q(id__icontains=q) |
                Q(user__username__icontains=q)
            )

        if start_dt:
            schools_qs = schools_qs.filter(created_at__gte=start_dt)
        if end_dt:
            schools_qs = schools_qs.filter(created_at__lte=end_dt)

        # latest assessment 子查询（你之前已有）
        latest_qs = Assessment.objects.filter(school_id=OuterRef("pk")).order_by("-updated_at")
        schools_qs = schools_qs.annotate(
            latest_assessment_id=Subquery(latest_qs.values("id")[:1]),
            latest_status=Subquery(latest_qs.values("status")[:1]),
            latest_level=Subquery(latest_qs.values("maturity_level")[:1]),
            latest_total_score=Subquery(latest_qs.values("total_score")[:1]),
            latest_updated_at=Subquery(latest_qs.values("updated_at")[:1]),
            latest_report_file=Subquery(latest_qs.values("report_file")[:1]),
        )

        school_rows = []
        if apply_status in ("", "approved"):
            for s in schools_qs:
                school_rows.append({
                    "id": s.id,
                    "name": s.name,
                    "school_type": s.school_type,
                    "province": s.province,
                    "city": s.city,
                    "district": s.district,
                    "contact_name": s.contact_name,
                    "contact_phone": s.contact_phone,
                    "contact_email": s.contact_email,
                    "username": getattr(s.user, "username", None),
                    "apply_status": "approved",
                    "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(s, "created_at", None) else None,
                    "latest_assessment": {
                        "id": getattr(s, "latest_assessment_id", None),
                        "status": getattr(s, "latest_status", None),
                        "maturity_level": getattr(s, "latest_level", None),
                        "total_score": getattr(s, "latest_total_score", None),
                        "updated_at": getattr(s, "latest_updated_at", None),
                        "report_file": getattr(s, "latest_report_file", None),
                    } if getattr(s, "latest_assessment_id", None) else None,
                    #  标识：这是 school 记录
                    "_row_type": "school",
                    "application_id": None,
                })

        # ============ 2) 待审核/已拒绝：AccountApplication ============
        # 用 province/city/district 与 region 匹配（你 application 里就是这三个字段）
        apps_qs = AccountApplication.objects.filter(
            province=region.province,
            city=region.city,
            district=region.name,
        ).order_by("-applied_at")

        if apply_status in ("pending", "rejected"):
            apps_qs = apps_qs.filter(status=apply_status)
        elif apply_status == "approved":
            apps_qs = apps_qs.none()  # approved 的申请不在这里展示（已转为 School）
        else:
            # apply_status 为空：把 pending + rejected 都带上
            apps_qs = apps_qs.filter(status__in=["pending", "rejected"])

        if school_type:
            apps_qs = apps_qs.filter(school_type=school_type)

        if q:
            apps_qs = apps_qs.filter(
                Q(school_name__icontains=q) |
                Q(contact_email__icontains=q) |
                Q(contact_phone__icontains=q) |
                Q(id__icontains=q)
            )
        if start_dt:
            apps_qs = apps_qs.filter(applied_at__gte=start_dt)
        if end_dt:
            apps_qs = apps_qs.filter(applied_at__lte=end_dt)

        app_rows = []
        for a in apps_qs:
            app_rows.append({
                "id": a.id,  #  这里 id 是 application 的 id（前端显示无所谓）
                "name": a.school_name,
                "school_type": a.school_type,
                "province": a.province,
                "city": a.city,
                "district": a.district,
                "contact_name": a.contact_name,
                "contact_phone": a.contact_phone,
                "contact_email": a.contact_email,
                "username": None,
                "apply_status": a.status,  # pending / rejected
                "created_at": a.applied_at.strftime("%Y-%m-%d %H:%M:%S") if a.applied_at else None,
                "latest_assessment": None,
                "_row_type": "application",
                "application_id": a.id,   #  给前端操作用
            })

        # 合并：申请放前面更合理（你也可以反过来）
        all_rows = app_rows + school_rows

        # 伪分页（合并后分页）
        total = len(all_rows)
        start = (page - 1) * page_size
        end = start + page_size
        page_rows = all_rows[start:end]

        return ok({
            "results": page_rows,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        })


class RegionAdminApplicationApproveView(RegionAdminBaseAPIView):
    """
    POST /api/region-admin/applications/<application_id>/approve/
    """
    def post(self, request, application_id: int):
        region = self.get_region(request)

        app = get_object_or_404(AccountApplication, id=application_id)

        if not (app.province == region.province and app.city == region.city and app.district == region.name):
            return bad("该申请不属于当前区县", code=http_status.HTTP_403_FORBIDDEN)

        if app.status != "pending":
            return bad("该申请已处理")

        if User.objects.filter(email=app.contact_email).exists():
            return bad("该邮箱已被注册，请联系管理员")

        try:
            with transaction.atomic():
                # 统一用户名/密码规则（最小改：改成你统一的生成器）
                username = gen_unique_school_username(app.school_name, User)
                password = gen_strong_password(8)

                user = User.objects.create_user(
                    username=username,
                    email=app.contact_email,
                    password=password,
                    role="school",
                )

                school = School.objects.create(
                    user=user,
                    region=region,
                    name=app.school_name,
                    school_type=app.school_type,
                    province=app.province,
                    city=app.city,
                    district=app.district,
                    contact_name=app.contact_name,
                    contact_position=app.contact_position,
                    contact_phone=app.contact_phone,
                    contact_email=app.contact_email,
                )

                app.status = "approved"
                app.reviewed_by = request.user
                app.reviewed_at = timezone.now()
                app.save(update_fields=["status", "reviewed_by", "reviewed_at"])

            #  邮件放在 atomic 外也行：失败不影响审批；但你要“账号邮件里包含密码”，必须保留 password
            email_sent = try_send_account_email(
                school_name=school.name,
                to_email=app.contact_email,
                username=username,
                password=password,
                log_prefix="RegionAdminApplicationApproveView",
            )

            msg = "审批成功" if email_sent else "审批成功（账号邮件发送失败，请手动告知学校账号信息）"
            return ok({"school_id": school.id, "username": username}, msg)

        except Exception as e:
            return bad(f"审批失败：{str(e)}", code=http_status.HTTP_500_INTERNAL_SERVER_ERROR)



class RegionAdminApplicationRejectView(RegionAdminBaseAPIView):
    """
    POST /api/region-admin/applications/<application_id>/reject/
    body: { reject_reason?: string }
    """
    def post(self, request, application_id: int):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

        try:
            app = AccountApplication.objects.get(id=application_id)
        except AccountApplication.DoesNotExist:
            return bad("申请不存在", code=http_status.HTTP_404_NOT_FOUND)

        if not (app.province == region.province and app.city == region.city and app.district == region.name):
            return bad("该申请不属于当前区县", code=http_status.HTTP_403_FORBIDDEN)

        if app.status != "pending":
            return bad("该申请已处理")

        reason = (request.data or {}).get("reject_reason", "")
        if not reason:
            return bad("请填写拒绝原因")

        app.status = "rejected"
        app.reject_reason = reason
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.save(update_fields=["status", "reject_reason", "reviewed_by", "reviewed_at"])

        return ok(None, "已拒绝申请")


class RegionAdminSchoolAssessmentsView(RegionAdminBaseAPIView):
    """
    GET /api/region-admin/schools/<school_id>/assessments/
    """
    def get(self, request, school_id: int):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

        # 强制区县范围
        try:
            school = School.objects.get(id=school_id, region=region)
        except School.DoesNotExist:
            return bad("学校不存在或不属于当前区县", code=http_status.HTTP_404_NOT_FOUND)

        qs = Assessment.objects.filter(school=school).order_by("-created_at")
        serializer = RegionAdminAssessmentListSerializer(qs, many=True)
        return ok(serializer.data)


class RegionAdminAssessmentDetailView(RegionAdminBaseAPIView):
    """
    GET /api/region-admin/assessments/<assessment_id>/
    """
    def get(self, request, assessment_id: int):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

        try:
            assessment = Assessment.objects.select_related("school").get(id=assessment_id, school__region=region)
        except Assessment.DoesNotExist:
            return bad("评估不存在或不属于当前区县", code=http_status.HTTP_404_NOT_FOUND)

        serializer = RegionAdminAssessmentDetailSerializer(assessment, context={"request": request})
        return ok(serializer.data)

class RegionAdminAssessmentListView(RegionAdminBaseAPIView):
    """
    GET /api/region-admin/assessments/
    query:
      - page, page_size
      - ordering: completed_at/-completed_at, created_at/-created_at, total_score/-total_score, school__name/-school__name
      - status
      - maturity_level
      - school_name (icontains)
      - has_report=true/false
    """
    def get(self, request):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

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

        start_at_str = request.query_params.get("start_at")
        end_at_str = request.query_params.get("end_at")

        if start_at_str:
            start_date = parse_date(start_at_str)
            if start_date:
                # 转化为当天 00:00:00
                start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
                qs = qs.filter(created_at__gte=start_datetime)

        if end_at_str:
            end_date = parse_date(end_at_str)
            if end_date:
                # 转化为当天 23:59:59，确保包含结束日期当天
                end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
                qs = qs.filter(created_at__lte=end_datetime)

        has_report = request.query_params.get("has_report")
        if has_report in ("true", "false"):
            if has_report == "true":
                qs = qs.exclude(report_file="").exclude(report_file__isnull=True)
            else:
                qs = qs.filter(Q(report_file="") | Q(report_file__isnull=True))

        school_type = request.query_params.get("school_type")
        if school_type:
            qs = qs.filter(school__school_type=school_type)

        # ---- ordering ----
        ordering = request.query_params.get("ordering") or "-completed_at,-created_at"
        allowed = {
            "completed_at", "-completed_at",
            "created_at", "-created_at",
            "total_score", "-total_score",
            "school__name", "-school__name",
            "status", "-status",
        }
        order_fields = [f.strip() for f in ordering.split(",") if f.strip() in allowed]
        if order_fields:
            qs = qs.order_by(*order_fields)
        else:
            qs = qs.order_by("-completed_at", "-created_at")

        # ---- summary（建议：基于过滤后的 qs）----
        summary = qs.aggregate(
            school_count=Count("school", distinct=True),
            has_assessment_count=Count("id"),
            completed_count=Count("id", filter=Q(status="completed")),
            report_count=Count(
                "id",
                filter=~Q(report_file="") & Q(report_file__isnull=False)
            ),
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
        return ok(data)

def _gen_school_username(region_code: str, email: str) -> str:
    h = hashlib.sha1(f"{region_code}:{email}".encode("utf-8")).hexdigest()[:10]
    return f"school_{region_code}_{h}"

class RegionAdminCreateSchoolView(RegionAdminBaseAPIView):
    """
    POST /api/region-admin/schools/
    区域管理员：新增学校（仅能加到自己区县）
    """
    def post(self, request):
        serializer = RegionAdminCreateSchoolSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        region = self.get_region(request)

        password = (data.get("password") or "").strip() or gen_strong_password(8)

        custom_username = (data.get("username") or "").strip()
        if custom_username:
            if not USERNAME_RE.match(custom_username):
                return APIResponse.error(message="用户名格式不合法（建议英文/数字/下划线，6-30位）", status_code=400)
            if User.objects.filter(username=custom_username).exists():
                return APIResponse.error(message="用户名已存在，请更换", status_code=400)
            username = custom_username
        else:
            username = gen_unique_school_username(data["name"], User)

        contact_email = data["contact_email"]  #

        if User.objects.filter(email=contact_email).exists():
            return APIResponse.error(message="该邮箱已被使用，请更换邮箱", status_code=400)

        user = User.objects.create_user(
            username=username,
            email=contact_email,
            password=password,
            role="school",
            is_active=True,
            is_staff=False,
        )
        user.is_locked = False
        user.locked_until = None
        user.save(update_fields=["is_locked", "locked_until"])

        school = School.objects.create(
            user=user,
            region=region,
            name=data["name"],
            school_type=data["school_type"],
            province=region.province,
            city=region.city,
            district=region.name,
            contact_name=data["contact_name"],
            contact_position=data["contact_position"],
            contact_phone=data["contact_phone"],
            contact_email=contact_email,
        )

        email_sent = try_send_account_email(
            school_name=school.name,
            to_email=contact_email,
            username=user.username,
            password=password,
            log_prefix="RegionAdminCreateSchoolView",
        )

        msg = "创建成功" if email_sent else "创建成功（账号邮件发送失败，请手动告知学校账号信息）"

        return ok(
            {"school_id": school.id, "username": user.username, "email": contact_email},
            message=msg
        )


from rest_framework import serializers

class RegionAdminResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=128)


class RegionAdminSchoolResetPasswordView(RegionAdminBaseAPIView):
    """
    POST /api/region-admin/schools/<school_id>/reset-password/
    body: { "password": "xxxxxx" }
    """
    def post(self, request, school_id: int):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

        # 限制只能操作自己区县的学校
        try:
            school = School.objects.select_related("user").get(id=school_id, region=region)
        except School.DoesNotExist:
            return bad("学校不存在或不属于当前区县", code=http_status.HTTP_404_NOT_FOUND)

        ser = RegionAdminResetPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        pwd = ser.validated_data["password"]
        school.user.set_password(pwd)
        school.user.save(update_fields=["password"])

        return ok({"school_id": school.id}, message="密码已更新")


class RegionAdminSchoolApproveView(RegionAdminBaseAPIView):
    """
    POST /api/region-admin/schools/<school_id>/approve/
    """
    def post(self, request, school_id: int):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

        school = get_object_or_404(School, id=school_id, region=region)

        # 你数据里 apply_status 是 approved/pending/rejected
        # 如果模型里没这个字段，这里就只做 user 激活即可
        update_fields = []

        if hasattr(school, "apply_status"):
            school.apply_status = "approved"
            update_fields.append("apply_status")

        # 同步激活账号
        if school.user_id:
            school.user.is_active = True
            school.user.save(update_fields=["is_active"])

        if update_fields:
            school.save(update_fields=update_fields)

        return ok({"school_id": school.id, "apply_status": getattr(school, "apply_status", "approved")})


class RegionAdminSchoolDeleteView(RegionAdminBaseAPIView):
    """
    DELETE /api/region-admin/schools/<school_id>/
    """
    def delete(self, request, school_id: int):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

        school = get_object_or_404(School, id=school_id, region=region)

        with transaction.atomic():
            # 先删 user（如果你希望保留 user，就删 school 即可）
            if school.user_id:
                school.user.delete()
            else:
                school.delete()

        return ok({"deleted": True, "school_id": school_id})

class RegionAdminApplicationDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsRegionAdmin]

    def delete(self, request, application_id: int):
        # 关键：只能删自己区县的申请
        # 你的 AccountApplication 如果没有 region 字段，就用 province/city/district 或者后续你合并列表时的规则做约束
        app = get_object_or_404(AccountApplication, id=application_id)

        # ✅ 如果你能拿到区域信息，建议做强校验：
        # region = request.user.managed_region
        # if app.province != region.province or app.city != region.city or app.district != region.name:
        #     return Response({"success": False, "message": "无权限删除其他区县申请"}, status=http_status.HTTP_403_FORBIDDEN)

        app.delete()
        return Response({"success": True, "message": "已删除申请记录", "data": None})

SCHOOL_TYPE_LABELS = {
    "primary": "小学",
    "junior": "初中",
    "senior": "高中",
    "nine_year": "九年一贯制",
    "twelve_year": "十二年一贯制",
}

TEMPLATE_HEADERS = [
    ("name", "学校名称*"),
    ("school_type", "学校类型*（primary/junior/senior/nine_year/twelve_year）"),
    ("contact_name", "联系人姓名*"),
    ("contact_position", "职务*"),
    ("contact_phone", "联系电话*"),
    ("contact_email", "联系邮箱（登录邮箱）*"),
    ("password", "初始密码*（不少于8位）"),
    ("username", "用户名（可选，不填自动生成）"),
]

class RegionAdminSchoolTemplateView(RegionAdminBaseAPIView):
    """
    GET /api/region-admin/schools/template/
    下载导入模板（xlsx）
    """
    def get(self, request):
        try:
            region = self.get_region(request)
        except ValueError as e:
            return bad(str(e), code=http_status.HTTP_403_FORBIDDEN)

        wb = Workbook()
        ws = wb.active
        ws.title = "schools"

        # 表头
        ws.append([h[1] for h in TEMPLATE_HEADERS])

        # 示例行
        ws.append([
            "示例学校",
            "primary",
            "张三",
            "信息中心主任",
            "13800000000",
            "demo_school@example.com",
            "Abcdef12",
            "",  # username 留空
        ])

        # 备注 sheet
        ws2 = wb.create_sheet("说明")
        ws2.append(["说明："])
        ws2.append([f"1）省/市/区县会自动使用你当前管理的区域：{region.province}-{region.city}-{region.name}"])
        ws2.append(["2）重复的联系邮箱（登录邮箱）会跳过"])
        ws2.append(["3）同一区域内学校名称重复会跳过"])
        ws2.append(["4）school_type 可选值：primary/junior/senior/nine_year/twelve_year"])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        resp = HttpResponse(
            buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = 'attachment; filename="schools_import_template.xlsx"'
        return resp


def _abbr_school_name(name: str) -> str:
    """
    生成学校名缩写：中文取每个字；英文取首字母；混合也尽量取字母/数字。
    你示例：XWZS... 这种更像 “玄武中学” -> XWZX，具体你可按需要替换更复杂的规则。
    这里先做一个稳的：取所有字母数字的大写前4位，不足就补X。
    """
    s = re.sub(r"[^A-Za-z0-9\u4e00-\u9fa5]", "", name or "")
    if not s:
        return "SCH"
    # 如果有英文/数字：优先取英数
    en = re.sub(r"[^A-Za-z0-9]", "", s).upper()
    if en:
        head = en[:4]
    else:
        # 全中文：简单用“拼音首字母”需要额外库，这里先取中文的前4个字的 unicode 方案不合适
        # 所以给一个保底：SCH
        head = "SCH"
    return (head + "XXXX")[:4]


class RegionAdminSchoolImportView(RegionAdminBaseAPIView):
    """
    POST /api/region-admin/schools/import/
    body: { rows: [ {...}, {...} ] }
    一次最多100条。重复学校名称自动跳过。
    """
    def post(self, request):
        region = self.get_region(request)  # 你基类已有

        rows = request.data.get("rows", [])
        if not isinstance(rows, list) or not rows:
            return bad("rows 不能为空", code=status.HTTP_400_BAD_REQUEST)

        if len(rows) > 100:
            rows = rows[:100]

        report = {
            "total": len(rows),
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "details": [],  # 每行返回：row_index, status, reason, school_id, username, password(可选)
        }

        # 用于“文件内重复”二次兜底（前端已经做了，这里再做一次更稳）
        seen_name = set()

        for idx, row in enumerate(rows):
            ser = RegionAdminSchoolImportRowSerializer(data=row)
            if not ser.is_valid():
                report["failed"] += 1
                report["details"].append({
                    "row_index": idx,
                    "status": "failed",
                    "reason": ser.errors,
                })
                continue

            data = ser.validated_data
            name = (data.get("name") or "").strip()
            norm_name = re.sub(r"\s+", "", name).lower()

            if not norm_name:
                report["failed"] += 1
                report["details"].append({
                    "row_index": idx,
                    "status": "failed",
                    "reason": "学校名称为空",
                })
                continue

            if norm_name in seen_name:
                report["skipped"] += 1
                report["details"].append({
                    "row_index": idx,
                    "status": "skipped",
                    "reason": "文件内学校名称重复，已跳过",
                })
                continue
            seen_name.add(norm_name)

            # 与数据库重名：跳过（按你规则）
            if School.objects.filter(region=region, name=name).exists():
                report["skipped"] += 1
                report["details"].append({
                    "row_index": idx,
                    "status": "skipped",
                    "reason": "同区域下已存在同名学校，已跳过",
                })
                continue

            # contact_email 用作 user.email（你已决定只保留 contact_email）
            contact_email = data["contact_email"]

            # email 唯一性（你之前 IntegrityError 就是这里）
            if User.objects.filter(email=contact_email).exists():
                report["failed"] += 1
                report["details"].append({
                    "row_index": idx,
                    "status": "failed",
                    "reason": "该邮箱已被注册（User.email 冲突）",
                })
                continue

            username = (data.get("username") or "").strip() or gen_unique_school_username(name, User)
            password = (data.get("password") or "").strip() or gen_strong_password(8)

            # username 唯一
            if User.objects.filter(username=username).exists():
                username = gen_unique_school_username(name, User)

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=contact_email,
                        password=password,
                        role="school",
                        is_active=True,
                        is_staff=False,
                    )
                    # 解锁字段（你已有这段）
                    user.is_locked = False
                    user.locked_until = None
                    user.save(update_fields=["is_locked", "locked_until"])

                    school = School.objects.create(
                        user=user,
                        region=region,
                        name=name,
                        school_type=data["school_type"],
                        province=region.province,
                        city=region.city,
                        district=region.name,  # 区县名称
                        contact_name=data["contact_name"],
                        contact_position=data["contact_position"],
                        contact_phone=data["contact_phone"],
                        contact_email=contact_email,
                    )

                report["created"] += 1

                email_sent = try_send_account_email(
                    school_name=school.name,
                    to_email=contact_email,
                    username=username,
                    password=password,
                    log_prefix="RegionAdminSchoolImportView",
                )

                # 这里把 password 返回给前端用于导入后展示（如果你不想回传可删掉 password）
                report["details"].append({
                    "row_index": idx,
                    "status": "created",
                    "school_id": school.id,
                    "username": username,
                    "password": password,
                    "email_sent": email_sent,
                })
            except Exception as e:
                report["failed"] += 1
                report["details"].append({
                    "row_index": idx,
                    "status": "failed",
                    "reason": str(e),
                })

        return ok(report)