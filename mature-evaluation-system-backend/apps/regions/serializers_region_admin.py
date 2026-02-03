from rest_framework import serializers
from apps.assessments.models import Assessment
from apps.schools.models import School
from apps.assessments.serializers import (
    InstitutionAssessmentSerializer,
    BehaviorAssessmentSerializer,
    AssetAssessmentSerializer,
    TechnologyAssessmentSerializer,
)

class RegionAdminSchoolListSerializer(serializers.ModelSerializer):
    latest_assessment = serializers.SerializerMethodField()

    # ✅ 账号
    username = serializers.CharField(source="user.username", read_only=True)

    # ✅ 联系方式（来自 School 表）
    contact_name = serializers.CharField(read_only=True)
    contact_phone = serializers.CharField(read_only=True)
    contact_email = serializers.CharField(read_only=True)

    # ✅ 申请时间（一般 School 会有 created_at；如果你字段名不同，告诉我我再对齐）
    created_at = serializers.DateTimeField(read_only=True)

    # ✅ 申请状态（如果你后端有真实字段 apply_status，就把这里改成直接读字段）
    apply_status = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "school_type",
            "province",
            "city",
            "district",

            "contact_name",
            "contact_phone",
            "contact_email",

            "username",
            "apply_status",
            "created_at",

            "latest_assessment",
        ]

    def get_apply_status(self, obj: School):
        # 你项目里 User 有 is_locked / locked_until / is_active（从你创建学校逻辑能看出来）
        u = getattr(obj, "user", None)
        if not u:
            return "unknown"

        # locked 优先
        if getattr(u, "is_locked", False):
            return "locked"

        # 正常情况：创建后就是 active
        if getattr(u, "is_active", False):
            return "approved"

        return "pending"

    def get_latest_assessment(self, obj: School):
        if getattr(obj, "latest_assessment_id", None) is None:
            return None
        return {
            "id": obj.latest_assessment_id,
            "status": obj.latest_status,
            "maturity_level": obj.latest_level,
            "total_score": obj.latest_total_score,
            "updated_at": obj.latest_updated_at,
            "report_file": obj.latest_report_file,
        }


class RegionAdminAssessmentListSerializer(serializers.ModelSerializer):
    school_id = serializers.IntegerField(source="school.id", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id", "school_id", "school_name",
            "status",
            "total_score", "maturity_level",
            "started_at", "completed_at", "created_at", "updated_at",
            "report_file",
        ]


class RegionAdminAssessmentDetailSerializer(serializers.ModelSerializer):
    school_id = serializers.IntegerField(source="school.id", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id",
            "school_id", "school_name",
            "status",
            "literacy_score", "institution_score", "behavior_score", "asset_score", "technology_score",
            "total_score", "maturity_level",
            "ai_suggestions",
            "report_file",
            "started_at", "completed_at", "created_at", "updated_at",
        ]


class RegionAssessmentListItemSerializer(serializers.ModelSerializer):
    school = serializers.SerializerMethodField()
    scores = serializers.SerializerMethodField()
    report = serializers.SerializerMethodField()
    times = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            "id",
            "status",
            "maturity_level",
            "school",
            "scores",
            "report",
            "times",
        ]

    def get_school(self, obj):
        s = obj.school
        return {
            "id": s.id,
            "name": s.name,
            "school_type": s.school_type,
        }

    def get_scores(self, obj):
        def s(v):
            return str(v) if v is not None else None

        return {
            "literacy_score": s(obj.literacy_score),
            "institution_score": s(obj.institution_score),
            "behavior_score": s(obj.behavior_score),
            "asset_score": s(obj.asset_score),
            "technology_score": s(obj.technology_score),
            "total_score": s(obj.total_score),
        }

    def get_report(self, obj):
        has_report = bool(obj.report_file)
        request = self.context.get("request")
        report_url = None
        if has_report and request:
            report_url = request.build_absolute_uri(obj.report_file.url)
        return {"has_report": has_report, "report_url": report_url}

    def get_times(self, obj):
        def fmt(dt):
            return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None

        return {
            "created_at": fmt(obj.created_at),
            "completed_at": fmt(obj.completed_at),
        }

class RegionAdminAssessmentDetailSerializer(serializers.ModelSerializer):
    school = serializers.SerializerMethodField()
    scores = serializers.SerializerMethodField()
    report = serializers.SerializerMethodField()
    times = serializers.SerializerMethodField()

    institution = serializers.SerializerMethodField()
    behavior = serializers.SerializerMethodField()
    asset = serializers.SerializerMethodField()
    technology = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            "id",
            "status",
            "maturity_level",
            "school",
            "scores",
            "report",
            "times",
            "institution",
            "behavior",
            "asset",
            "technology",
        ]

    def get_school(self, obj):
        s = obj.school
        return {
            "id": s.id,
            "name": s.name,
            "school_type": s.school_type,
            "province": s.province,
            "city": s.city,
            "district": s.district,
        }

    def get_scores(self, obj):
        def s(v):
            return str(v) if v is not None else None
        return {
            "literacy_score": s(obj.literacy_score),
            "institution_score": s(obj.institution_score),
            "behavior_score": s(obj.behavior_score),
            "asset_score": s(obj.asset_score),
            "technology_score": s(obj.technology_score),
            "total_score": s(obj.total_score),
        }

    def get_report(self, obj):
        has_report = bool(obj.report_file)
        request = self.context.get("request")
        report_url = None
        if has_report and request:
            report_url = request.build_absolute_uri(obj.report_file.url)
        return {"has_report": has_report, "report_url": report_url}

    def get_times(self, obj):
        def fmt(dt):
            return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None
        return {
            "started_at": fmt(obj.started_at),
            "completed_at": fmt(obj.completed_at),
            "created_at": fmt(obj.created_at),
            "updated_at": fmt(obj.updated_at),
        }

    def get_institution(self, obj):
        if hasattr(obj, "institution"):
            return InstitutionAssessmentSerializer(obj.institution).data
        return None

    def get_behavior(self, obj):
        if hasattr(obj, "behavior"):
            return BehaviorAssessmentSerializer(obj.behavior).data
        return None

    def get_asset(self, obj):
        if hasattr(obj, "asset"):
            return AssetAssessmentSerializer(obj.asset).data
        return None

    def get_technology(self, obj):
        if hasattr(obj, "technology"):
            return TechnologyAssessmentSerializer(obj.technology).data
        return None


class RegionAdminSchoolImportRowSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    school_type = serializers.CharField(required=True)
    contact_name = serializers.CharField(required=True)
    contact_position = serializers.CharField(required=True)
    contact_phone = serializers.CharField(required=True)
    contact_email = serializers.EmailField(required=True)

    # 可选：区域管理员支持自定义账号密码
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)