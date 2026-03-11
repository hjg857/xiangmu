from typing import Any, Dict, List, Tuple
from apps.surveys.models import SurveyInstance


def _is_blank(val: Any) -> bool:
    """只把 None / 空字符串 / 空列表判为未填；0/False 都算已填。"""
    if val is None:
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    if isinstance(val, (list, tuple, dict)) and len(val) == 0:
        return True
    return False


def _require(instance: Any, fields: List[str]) -> Tuple[bool, List[str]]:
    """instance 存在且 fields 都不空 => True"""
    if not instance:
        return False, fields
    missing = []
    for f in fields:
        if _is_blank(getattr(instance, f, None)):
            missing.append(f)
    return (len(missing) == 0), missing


def compute_module_status(assessment) -> Dict[str, bool]:
    """
    规则：
    - literacy：三类问卷都 collected_count > 0
    - institution/behavior/asset/technology：必填 + 条件必填
    """
    # -------------------------
    # A) 数据素养：问卷 collected_count > 0
    # -------------------------
    instances = (
        SurveyInstance.objects
        .filter(assessment=assessment)
        .select_related("template")
    )

    def survey_ok(survey_type: str) -> bool:
        inst = next(
            (x for x in instances if x.template and x.template.survey_type == survey_type),
            None
        )
        return bool(inst and (inst.collected_count or 0) > 0)

    literacy_ok = survey_ok("teacher") and survey_ok("student") and survey_ok("manager")

    # -------------------------
    # B) 数据制度：必填 + 条件必填
    # -------------------------
    institution = getattr(assessment, "institution", None)

    # 基础必填（你可按“表单里你认为必填的”来调整）
    base_ok, _ = _require(institution, [
        "has_leadership_group",
        "meeting_activity_count",
        "has_data_staff",
        "has_training",
        "has_management_doc",
        "has_practice_doc",
    ])

    cond_ok = True

    # 条件：配备数据管理人员 => 专/兼职人数必填
    if institution and institution.has_data_staff is True:
        ok, _ = _require(institution, ["fulltime_staff_count", "parttime_staff_count"])
        cond_ok = cond_ok and ok

    # 条件：参与培训 => 培训次数 + 证书数量必填
    if institution and institution.has_training is True:
        ok, _ = _require(institution, [
            "training_count",
            "national_cert_count",
            "provincial_cert_count",
            "city_cert_count",
        ])
        cond_ok = cond_ok and ok

    # 条件：出台管理文件 => 数量 + 文件列表必填（analysis 文本不强制）
    if institution and institution.has_management_doc is True:
        ok, _ = _require(institution, ["management_doc_count", "management_doc_files"])
        cond_ok = cond_ok and ok

    # 条件：出台实践指导文件 => 数量 + 文件列表必填
    if institution and institution.has_practice_doc is True:
        ok, _ = _require(institution, ["practice_doc_count", "practice_doc_files"])
        cond_ok = cond_ok and ok

    institution_ok = base_ok and cond_ok

    # -------------------------
    # C) 数据行为：全部填写（允许 0）
    # -------------------------
    behavior = getattr(assessment, "behavior", None)
    behavior_ok, _ = _require(behavior, [
        # 1. 行为监测
        "teacher_login_freq",
        "student_login_freq",
        "manager_login_freq",
        "visit_count",
        # 2. 应用成效（全部都要填；你如果某些不想强制，可从这里删）
        "published_paper_count",
        "published_book_count",
        "case_national_count",
        "case_provincial_count",
        "case_city_count",
        "award_national_count",
        "award_provincial_count",
        "award_city_count",
        "media_national_count",
        "media_provincial_count",
        "media_city_count",
        "conference_national_count",
        "conference_provincial_count",
        "conference_city_count",
    ])

    # -------------------------
    # D) 数据资产：四个量都填（允许 0.00）
    # -------------------------
    asset = getattr(assessment, "asset", None)
    asset_ok, _ = _require(asset, [
        "management_data_volume",
        "resource_data_volume",
        "service_data_volume",
        "other_data_volume",
    ])

    # -------------------------
    # E) 数据技术：全部填写（含你新增 cloud_dedicated_service）
    # -------------------------
    from apps.assessments.models import TechnologyAssessment

    # 强制重新获取最新的字典数据，打印 ID 确保对齐
    tech_data = TechnologyAssessment.objects.filter(assessment_id=assessment.id).values().first()

    technology_ok = False
    if tech_data:
        # 关键：从字典直接取值
        has_center = tech_data.get('has_independent_data_center')

        # 1. 基础项：排除 has_independent_data_center 后单独判断
        # 这里必须使用 _is_blank 的严格判断，确保 0 或 False 算已填
        base_fields = [
            "student_device_ratio",
            "teacher_device_ratio",
            "has_data_platform",
            "security_certified_count",
            "security_certified_ratio",
            "has_security_incident",
        ]

        # 只要 has_center 不是 None（可以是 False 或 True），就算第一步过了
        base_ok = (has_center is not None)
        for f in base_fields:
            if _is_blank(tech_data.get(f)):
                base_ok = False
                break

        # 2. 条件项：二选一
        cond_ok = False
        if has_center is True:
            cond_ok = not _is_blank(tech_data.get('data_center_standard'))
        elif has_center is False:
            cond_ok = not _is_blank(tech_data.get('cloud_dedicated_service'))

        technology_ok = bool(base_ok and cond_ok)

        # 打印这一行，在终端看 ID 是否和你浏览器里的 ID (19) 一致
        if not technology_ok:
            print(f"--- 正在诊断评估ID: {assessment.id} ---")
            print(f"has_center值: {has_center}, 基础项通过: {base_ok}, 条件项通过: {cond_ok}")
    else:
        # 如果进到这里，说明数据库里根本没这条技术评估记录
        technology_ok = False

    return {
        "literacy": literacy_ok,
        "institution": institution_ok,
        "behavior": behavior_ok,
        "asset": asset_ok,
        "technology": technology_ok,
    }
