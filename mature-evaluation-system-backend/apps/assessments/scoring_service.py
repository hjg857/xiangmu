"""
评估计分服务
实现五个维度的计分逻辑

计分公式说明（按老师要求）：
=================================
1. 观测点标准化: C_k = (C_i / S_i) × 5
   - C_i: 观测点实际得分
   - S_i: 观测点满分
   - C_k: 标准化后得分，满分5分

2. 二级指标得分: Σ(C_k × γ_k)
   - γ_k: 观测点权重（同一二级指标下的观测点权重和=1）
   - 满分5分

3. 一级指标得分: Σ(二级得分 × β_j)
   - β_j: 二级指标权重（同一一级指标下的二级权重和=1）
   - 满分5分

4. 总分: Σ(一级得分 × α_i)
   - α_i: 一级指标权重（五个维度权重和=1）
   - 满分5分
=================================
"""
from decimal import Decimal
from typing import Dict, List
import logging
from . import scoring_config as config

logger = logging.getLogger(__name__)


class ScoringService:
    """评估计分服务类"""
    
    def __init__(self, assessment):
        self.assessment = assessment
        self.school = assessment.school
        self.observation_scores = {}  # 观测点得分（5分制）
        self.secondary_scores = {}    # 二级指标得分（5分制）
        self.dimension_scores = {}    # 一级维度得分（5分制）

    def calculate_all_scores(self) -> Dict[str, Decimal]:
        """
        计算所有维度得分
        返回: 各维度得分（5分制）和总分（5分制）
        """
        logger.info(f"开始计算评估 {self.assessment.id} 的得分")

        # 计算各维度得分（5分制）
        a_score = self.calculate_literacy_score()      # A 数据素养
        b_score = self.calculate_institution_score()   # B 数据制度
        c_score = self.calculate_behavior_score()      # C 数据行为
        d_score = self.calculate_asset_score()         # D 数据资产
        e_score = self.calculate_technology_score()    # E 数据技术

        # 存储一级维度得分
        self.dimension_scores = {
            'A': float(a_score),
            'B': float(b_score),
            'C': float(c_score),
            'D': float(d_score),
            'E': float(e_score),
        }

        # 计算总分（5分制）: Σ(一级得分 × α_i)
        total_score_5 = (
            float(a_score) * config.DIMENSION_WEIGHTS['A'] +
            float(b_score) * config.DIMENSION_WEIGHTS['B'] +
            float(c_score) * config.DIMENSION_WEIGHTS['C'] +
            float(d_score) * config.DIMENSION_WEIGHTS['D'] +
            float(e_score) * config.DIMENSION_WEIGHTS['E']
        )

        scores = {
            'literacy_score': Decimal(str(round(float(a_score), 4))),
            'institution_score': Decimal(str(round(float(b_score), 4))),
            'behavior_score': Decimal(str(round(float(c_score), 4))),
            'asset_score': Decimal(str(round(float(d_score), 4))),
            'technology_score': Decimal(str(round(float(e_score), 4))),
            'total_score': Decimal(str(round(total_score_5, 4))),
        }

        # 确定成熟度等级（基于5分制）
        scores['maturity_level'] = self.determine_maturity_level(total_score_5)

        logger.info(f"评估 {self.assessment.id} 计分完成:")
        logger.info(f"  A数据素养={a_score:.4f}, B数据制度={b_score:.4f}, C数据行为={c_score:.4f}")
        logger.info(f"  D数据资产={d_score:.4f}, E数据技术={e_score:.4f}")
        logger.info(f"  总分={total_score_5:.4f}（5分制）, 等级={scores['maturity_level']}")
        
        return scores

    def _normalize_score(self, raw_score: float, max_score: float) -> float:
        """
        观测点标准化: C_k = (C_i / S_i) × 5
        返回: 0-5分
        """
        if max_score <= 0:
            return 0.0
        normalized = (raw_score / max_score) * 5.0
        return min(normalized, 5.0)

    def _calculate_secondary_score(self, observation_scores: Dict[str, float], 
                                   observation_keys: List[str]) -> float:
        """
        计算二级指标得分: Σ(C_k × γ_k)
        observation_scores: {观测点编号: 5分制得分}
        observation_keys: 该二级指标包含的观测点编号列表
        返回: 0-5分
        """
        total = 0.0
        for key in observation_keys:
            score = observation_scores.get(key, 0.0)
            weight = config.OBSERVATION_WEIGHTS.get(key, 0.0)
            total += score * weight
        return total

    def _calculate_dimension_score(self, secondary_scores: Dict[str, float],
                                   secondary_keys: List[str]) -> float:
        """
        计算一级维度得分: Σ(二级得分 × β_j)
        secondary_scores: {二级指标编号: 5分制得分}
        secondary_keys: 该一级维度包含的二级指标编号列表
        返回: 0-5分
        """
        total = 0.0
        for key in secondary_keys:
            score = secondary_scores.get(key, 0.0)
            weight = config.SECONDARY_WEIGHTS.get(key, 0.0)
            total += score * weight
        return total

    def calculate_literacy_score(self) -> float:
        """
        计算A维度-数据素养得分（5分制）
        包含: A1教师、A2管理者、A3学生
        """
        logger.info("计算数据素养得分")
        from apps.surveys.models import SurveyInstance, SurveyResponse

        # 获取问卷实例
        teacher_instances = SurveyInstance.objects.filter(
            assessment=self.assessment, template__survey_type='teacher')
        manager_instances = SurveyInstance.objects.filter(
            assessment=self.assessment, template__survey_type='manager')
        student_instances = SurveyInstance.objects.filter(
            assessment=self.assessment, template__survey_type='student')

        # 计算各观测点得分（5分制）
        self._calc_literacy_observations('teacher', teacher_instances)
        self._calc_literacy_observations('manager', manager_instances)
        self._calc_literacy_observations('student', student_instances)

        # 计算二级指标得分
        a1_score = self._calculate_secondary_score(
            self.observation_scores, ['A11', 'A12', 'A13', 'A14', 'A15'])
        a2_score = self._calculate_secondary_score(
            self.observation_scores, ['A21', 'A22', 'A23', 'A24', 'A25'])
        a3_score = self._calculate_secondary_score(
            self.observation_scores, ['A31', 'A32', 'A33', 'A34', 'A35'])

        self.secondary_scores['A1'] = a1_score
        self.secondary_scores['A2'] = a2_score
        self.secondary_scores['A3'] = a3_score

        # 计算一级维度得分
        dimension_score = self._calculate_dimension_score(
            self.secondary_scores, ['A1', 'A2', 'A3'])

        logger.info(f"A维度: A1={a1_score:.4f}, A2={a2_score:.4f}, A3={a3_score:.4f}, 维度得分={dimension_score:.4f}")
        return dimension_score

    def _calc_literacy_observations(self, survey_type: str, instances) -> None:
        """计算数据素养问卷的观测点得分"""
        from apps.surveys.models import SurveyResponse
        
        survey_config = config.LITERACY_SURVEY_CONFIG.get(survey_type, {})
        
        responses = []
        for instance in instances:
            responses.extend(SurveyResponse.objects.filter(instance=instance))

        if not responses:
            logger.warning(f"没有{survey_type}问卷回答数据")
            for point_name in survey_config.keys():
                self.observation_scores[point_name] = 0.0
            return

        for point_name, point_config in survey_config.items():
            start, end = point_config['range']
            questions = list(range(start, end + 1))
            max_score = point_config['max_score']

            raw_score = self._calc_survey_raw_score(responses, questions)
            normalized = self._normalize_score(raw_score, max_score)
            self.observation_scores[point_name] = normalized
            
            logger.debug(f"{point_name}: 原始={raw_score:.2f}/{max_score}, 标准化={normalized:.4f}")

    def _calc_survey_raw_score(self, responses: List, question_nums: List[int]) -> float:
        """计算问卷题目的原始平均得分"""
        if not responses:
            return 0.0

        total_score = 0
        response_count = 0

        for response in responses:
            answers = response.answers or {}
            for q_num in question_nums:
                q_key = f'q{q_num}'
                if q_key in answers:
                    answer_value = answers[q_key]
                    if isinstance(answer_value, str):
                        total_score += config.SCALE_SCORE_MAPPING.get(answer_value, 0)
                    else:
                        total_score += int(answer_value)
            response_count += 1

        return total_score / response_count if response_count > 0 else 0.0

    def calculate_institution_score(self) -> float:
        """
        计算B维度-数据制度得分（5分制）
        包含: B1数据组织机构、B2数据人员配备、B3数据管理文件
        """
        logger.info("计算数据制度得分")

        try:
            inst = self.assessment.institution
        except:
            logger.warning("没有数据制度评估数据")
            return 0.0

        rules = config.INSTITUTION_SCORING_RULES

        # B11: 数据领导/工作小组
        b11_raw = rules['B11']['rules'].get(inst.has_leadership_group, 0)
        self.observation_scores['B11'] = self._normalize_score(b11_raw, rules['B11']['max_score'])

        # B12: 数据组织运行情况
        b12_raw = self._apply_range_rules(inst.meeting_activity_count or 0, rules['B12']['rules'])
        self.observation_scores['B12'] = self._normalize_score(b12_raw, rules['B12']['max_score'])

        # B21: 数据专职/兼职管理人员
        if not inst.has_data_staff:
            b21_raw = 0
        else:
            staff_score = min((inst.fulltime_staff_count or 0) * 5 + (inst.parttime_staff_count or 0) * 3, 10)
            resp_score = 10 if inst.has_clear_responsibilities else 0
            b21_raw = staff_score + resp_score
        self.observation_scores['B21'] = self._normalize_score(b21_raw, rules['B21']['max_score'])

        # B22: 数据人员进修与培训
        if not inst.has_training:
            b22_raw = 0
        else:
            training_rules = [r for r in rules['B22']['sub_items'] if r.get('field') == 'training_count'][0]
            training_score = self._apply_range_rules(inst.training_count or 0, training_rules['rules'])
            cert_score = min((inst.national_cert_count or 0) * 5 + (inst.provincial_cert_count or 0) * 3 + (inst.city_cert_count or 0), 20)
            b22_raw = training_score + cert_score
        self.observation_scores['B22'] = self._normalize_score(b22_raw, rules['B22']['max_score'])

        # B31: 数据管理制度类文件
        if not inst.has_management_doc:
            b31_raw = 0
        else:
            doc_count = inst.management_doc_count or 0
            doc_score = min(doc_count * 5, 20)
            quality_score = self._score_documents_with_llm(inst.management_doc_files, 'management', 20, inst)
            b31_raw = doc_score + quality_score
        self.observation_scores['B31'] = self._normalize_score(b31_raw, rules['B31']['max_score'])

        # B32: 数据实践指导类文件
        if not inst.has_practice_doc:
            b32_raw = 0
        else:
            doc_count = inst.practice_doc_count or 0
            doc_score = min(doc_count * 5, 20)
            quality_score = self._score_documents_with_llm(inst.practice_doc_files, 'practice', 20, inst)
            b32_raw = doc_score + quality_score
        self.observation_scores['B32'] = self._normalize_score(b32_raw, rules['B32']['max_score'])

        # 计算二级指标得分
        b1_score = self._calculate_secondary_score(self.observation_scores, ['B11', 'B12'])
        b2_score = self._calculate_secondary_score(self.observation_scores, ['B21', 'B22'])
        b3_score = self._calculate_secondary_score(self.observation_scores, ['B31', 'B32'])

        self.secondary_scores['B1'] = b1_score
        self.secondary_scores['B2'] = b2_score
        self.secondary_scores['B3'] = b3_score

        # 计算一级维度得分
        dimension_score = self._calculate_dimension_score(self.secondary_scores, ['B1', 'B2', 'B3'])

        logger.info(f"B维度: B1={b1_score:.4f}, B2={b2_score:.4f}, B3={b3_score:.4f}, 维度得分={dimension_score:.4f}")
        return dimension_score

    def calculate_behavior_score(self) -> float:
        """
        计算C维度-数据行为得分（5分制）
        包含: C1数据行为监测、C2数据应用成效
        """
        logger.info("计算数据行为得分")

        try:
            behavior = self.assessment.behavior
        except:
            logger.warning("没有数据行为评估数据")
            return 0.0

        rules = config.BEHAVIOR_SCORING_RULES

        # C11: 教师数据行为
        c11_raw = self._apply_range_rules(behavior.teacher_login_freq or 0, rules['C11']['rules'])
        self.observation_scores['C11'] = self._normalize_score(c11_raw, rules['C11']['max_score'])

        # C12: 学生数据行为
        c12_raw = self._apply_range_rules(behavior.student_login_freq or 0, rules['C12']['rules'])
        self.observation_scores['C12'] = self._normalize_score(c12_raw, rules['C12']['max_score'])

        # C13: 管理者数据行为
        c13_raw = self._apply_range_rules(behavior.manager_login_freq or 0, rules['C13']['rules'])
        self.observation_scores['C13'] = self._normalize_score(c13_raw, rules['C13']['max_score'])

        # C21: 数据应用特色成果
        c21_raw = 0
        for sub_item in rules['C21']['sub_items']:
            sub_score = sum((getattr(behavior, f, None) or 0) * s for f, s in sub_item['fields'].items())
            c21_raw += min(sub_score, sub_item['max_score'])
        self.observation_scores['C21'] = self._normalize_score(c21_raw, rules['C21']['max_score'])

        # C22: 数据应用社会影响
        c22_raw = 0
        for sub_item in rules['C22']['sub_items']:
            if 'fields' in sub_item:
                sub_score = sum((getattr(behavior, f, None) or 0) * s for f, s in sub_item['fields'].items())
                c22_raw += min(sub_score, sub_item['max_score'])
            elif 'field' in sub_item:
                field_val = getattr(behavior, sub_item['field'], None) or 0
                c22_raw += min(field_val * sub_item['score_per_visit'], sub_item['max_score'])
        self.observation_scores['C22'] = self._normalize_score(c22_raw, rules['C22']['max_score'])

        # C23: 应用效果主观评价（来自问卷）
        c23_raw = self._calc_application_effect_score()
        self.observation_scores['C23'] = self._normalize_score(c23_raw, rules['C23']['max_score'])

        # 计算二级指标得分
        c1_score = self._calculate_secondary_score(self.observation_scores, ['C11', 'C12', 'C13'])
        c2_score = self._calculate_secondary_score(self.observation_scores, ['C21', 'C22', 'C23'])

        self.secondary_scores['C1'] = c1_score
        self.secondary_scores['C2'] = c2_score

        # 计算一级维度得分
        dimension_score = self._calculate_dimension_score(self.secondary_scores, ['C1', 'C2'])

        logger.info(f"C维度: C1={c1_score:.4f}, C2={c2_score:.4f}, 维度得分={dimension_score:.4f}")
        return dimension_score

    def _calc_application_effect_score(self) -> float:
        """计算C23应用效果主观评价得分"""
        from apps.surveys.models import SurveyInstance, SurveyResponse
        
        c23_config = config.BEHAVIOR_SCORING_RULES['C23']
        survey_ranges = c23_config['survey_ranges']
        total = 0.0

        for survey_type, (start, end) in survey_ranges.items():
            instances = SurveyInstance.objects.filter(
                assessment=self.assessment, template__survey_type=survey_type)
            responses = []
            for inst in instances:
                responses.extend(SurveyResponse.objects.filter(instance=inst))
            total += self._calc_survey_raw_score(responses, list(range(start, end + 1)))

        return total

    def calculate_asset_score(self) -> float:
        """
        计算D维度-数据资产得分（5分制）
        包含: D1数据资产意识、D2数据资产积累
        """
        logger.info("计算数据资产得分")

        try:
            asset = self.assessment.asset
        except:
            logger.warning("没有数据资产评估数据")
            return 0.0

        from apps.surveys.models import SurveyInstance, SurveyResponse
        rules = config.ASSET_SCORING_RULES

        # 获取管理者问卷回答
        manager_instances = SurveyInstance.objects.filter(
            assessment=self.assessment, template__survey_type='manager')
        manager_responses = []
        for inst in manager_instances:
            manager_responses.extend(SurveyResponse.objects.filter(instance=inst))

        # D11: 数据资产价值意识
        start, end = rules['D11']['survey_range']
        d11_raw = self._calc_survey_raw_score(manager_responses, list(range(start, end + 1)))
        self.observation_scores['D11'] = self._normalize_score(d11_raw, rules['D11']['max_score'])

        # D12: 数据资产应用意识
        start, end = rules['D12']['survey_range']
        d12_raw = self._calc_survey_raw_score(manager_responses, list(range(start, end + 1)))
        self.observation_scores['D12'] = self._normalize_score(d12_raw, rules['D12']['max_score'])

        # D13: 数据资产治理意识
        start, end = rules['D13']['survey_range']
        d13_raw = self._calc_survey_raw_score(manager_responses, list(range(start, end + 1)))
        self.observation_scores['D13'] = self._normalize_score(d13_raw, rules['D13']['max_score'])

        # D21: 数据资产总量
        total_volume = float((asset.management_data_volume or 0) + (asset.resource_data_volume or 0) + 
                            (asset.service_data_volume or 0) + (asset.other_data_volume or 0))
        d21_raw = self._apply_range_rules(total_volume, rules['D21']['rules'])
        self.observation_scores['D21'] = self._normalize_score(d21_raw, rules['D21']['max_score'])


        # 计算二级指标得分
        d1_score = self._calculate_secondary_score(self.observation_scores, ['D11', 'D12', 'D13'])
        d2_score = self._calculate_secondary_score(self.observation_scores, ['D21'])

        self.secondary_scores['D1'] = d1_score
        self.secondary_scores['D2'] = d2_score

        # 计算一级维度得分
        dimension_score = self._calculate_dimension_score(self.secondary_scores, ['D1', 'D2'])

        logger.info(f"D维度: D1={d1_score:.4f}, D2={d2_score:.4f}, 维度得分={dimension_score:.4f}")
        return dimension_score

    def calculate_technology_score(self) -> float:
        """
        计算E维度-数据技术得分（5分制）
        包含: E1数据基础设施、E2数据安保水平
        """
        logger.info("计算数据技术得分")

        try:
            tech = self.assessment.technology
        except:
            logger.warning("没有数据技术评估数据")
            return 0.0

        rules = config.TECHNOLOGY_SCORING_RULES

        # E11: 数据硬件设施
        e11_raw = 0
        for sub_item in rules['E11']['sub_items']:
            field_value = getattr(tech, sub_item['field'], None)
            if field_value and field_value in sub_item['rules']:
                e11_raw += sub_item['rules'][field_value]
        self.observation_scores['E11'] = self._normalize_score(e11_raw, rules['E11']['max_score'])

        # E12: 数据系统平台
        e12_raw = rules['E12']['rules'].get(tech.has_data_platform, 0)
        self.observation_scores['E12'] = self._normalize_score(e12_raw, rules['E12']['max_score'])

        e13_raw = rules['E13']['rules'].get(tech.cloud_dedicated_service, 0)
        self.observation_scores['E13'] = self._normalize_score(e13_raw, rules['E13']['max_score'])

        # E21: 数据安全合规与认证
        e21_raw = 0
        for sub_item in rules['E21']['sub_items']:
            field_value = getattr(tech, sub_item['field'], None)
            if sub_item['field'] == 'security_certified_count':
                e21_raw += self._apply_range_rules(field_value or 0, sub_item['rules'])
            elif field_value and field_value in sub_item['rules']:
                e21_raw += sub_item['rules'][field_value]
        self.observation_scores['E21'] = self._normalize_score(e21_raw, rules['E21']['max_score'])

        # E22: 数据风险事件记录（扣分项）
        # 如果发生过风险事件，E22得分为0；否则满分
        # 注意：这里不用负分，而是用0分表示扣分效果
        if tech.has_security_incident:
            self.observation_scores['E22'] = 0.0  # 发生过事件，该项0分
        else:
            self.observation_scores['E22'] = 5.0  # 未发生或未填写，满分5分

        # 计算二级指标得分
        e1_score = self._calculate_secondary_score(self.observation_scores, ['E11', 'E12'])
        e2_score = self._calculate_secondary_score(self.observation_scores, ['E21', 'E22'])
        e3_score = self._calculate_secondary_score(self.observation_scores, ['E13'])

        self.secondary_scores['E1'] = e1_score
        self.secondary_scores['E2'] = e2_score
        self.secondary_scores['E3'] = e3_score

        # 计算一级维度得分
        dimension_score = self._calculate_dimension_score(self.secondary_scores, ['E1', 'E2', 'E3'])

        logger.info(f"E维度: E1={e1_score:.4f}, E2={e2_score:.4f}, E3={e3_score:.4f}, 维度得分={dimension_score:.4f}")
        return dimension_score

    def _apply_range_rules(self, value: float, rules: List[Dict]) -> float:
        """应用范围规则计算得分"""
        for rule in rules:
            cond = rule['condition']
            if cond == 'lt' and value < rule['value']:
                return rule['score']
            elif cond == 'lte' and value <= rule['value']:
                return rule['score']
            elif cond == 'gt' and value > rule['value']:
                return rule['score']
            elif cond == 'gte' and value >= rule['value']:
                return rule['score']
            elif cond == 'between':
                min_val = rule.get('min', float('-inf'))
                max_val = rule.get('max', float('inf'))
                if min_val <= value <= max_val:
                    return rule['score']
        return 0.0

    def determine_maturity_level(self, total_score: float) -> str:
        """
        根据总分（5分制）确定成熟度等级
        等级划分（基于5分制）:
        - 引领级: 4.5-5.0
        - 成熟级: 4.0-4.5
        - 成长级: 3.5-4.0
        - 初始级: 0-3.5
        """
        if total_score >= 4.5:
            return 'leading'
        elif total_score >= 4.0:
            return 'mature'
        elif total_score >= 3.5:
            return 'growing'
        else:
            return 'initial'

    def _score_documents_with_llm(self, doc_files: list, doc_type: str, 
                                   max_score: float = 20.0, institution=None) -> float:
        """使用大模型评分文档质量"""
        from apps.admin_panel.models import SystemConfig
        from .llm_service import LLMService

        # 检查缓存
        if institution:
            cached = getattr(institution, f'{doc_type}_doc_analysis', '') or ''
            if cached.strip():
                logger.info(f"使用缓存的{doc_type}文件分析结果")
                return max_score * 0.75 if doc_files else 0.0

        # 检查是否启用大模型
        llm_enabled = SystemConfig.get_config('llm_enabled', None)
        if llm_enabled is None:
            from django.conf import settings
            llm_enabled = bool(getattr(settings, 'DEEPSEEK_API_KEY', ''))

        if not llm_enabled or not doc_files:
            return max_score / 2.0 if doc_files else 0.0

        try:
            llm_service = LLMService()
            total_score = 0
            scored_count = 0
            all_analysis = []

            for doc_info in doc_files:
                try:
                    file_path = doc_info.get('path') or doc_info.get('url')
                    if not file_path:
                        continue

                    content = self._read_file_content(file_path)
                    if not content:
                        continue

                    if doc_type == 'management':
                        result = llm_service.score_management_document(content, max_score=max_score)
                    else:
                        result = llm_service.score_practice_document(content, max_score=max_score)

                    if result['success']:
                        total_score += result['score']
                        scored_count += 1
                        all_analysis.append(f"【{doc_info.get('name', '未知')}】\n{result.get('analysis', '')}")
                    else:
                        total_score += max_score / 2.0
                        scored_count += 1
                except Exception as e:
                    logger.error(f"评分文件出错: {e}")
                    total_score += max_score / 2.0
                    scored_count += 1

            # 保存分析结果
            if institution and all_analysis:
                try:
                    setattr(institution, f'{doc_type}_doc_analysis', '\n\n'.join(all_analysis))
                    institution.save(update_fields=[f'{doc_type}_doc_analysis'])
                except Exception as e:
                    logger.error(f"保存分析结果失败: {e}")

            return min(total_score / scored_count, max_score) if scored_count > 0 else max_score / 2.0

        except Exception as e:
            logger.error(f"大模型评分出错: {e}")
            return max_score / 2.0

    def _read_file_content(self, file_path: str) -> str:
        """读取文件内容"""
        from django.core.files.storage import default_storage
        import os

        try:
            if file_path.startswith('/media/'):
                file_path = file_path.replace('/media/', '')
            elif file_path.startswith('http'):
                from urllib.parse import urlparse
                file_path = urlparse(file_path).path.replace('/media/', '')

            if not default_storage.exists(file_path):
                return ""

            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                return self._extract_pdf_content(file_path)
            elif file_ext in ['.docx', '.doc']:
                return self._extract_docx_content(file_path)
            else:
                with default_storage.open(file_path, 'rb') as f:
                    content = self._decode_content(f.read(), file_path)

            return content[:8000] + "\n...(已截断)" if len(content) > 8000 else content

        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return ""

    def _decode_content(self, content_bytes: bytes, file_path: str) -> str:
        """尝试多种编码解码"""
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin-1']:
            try:
                return content_bytes.decode(encoding)
            except:
                continue
        return ""

    def _extract_pdf_content(self, file_path: str) -> str:
        """提取PDF内容"""
        try:
            import PyPDF2
            from django.core.files.storage import default_storage
            with default_storage.open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return '\n'.join(page.extract_text() for page in reader.pages)
        except ImportError:
            return "PDF文件（需安装PyPDF2）"
        except Exception as e:
            return f"PDF提取失败: {e}"

    def _extract_docx_content(self, file_path: str) -> str:
        """提取DOCX内容"""
        try:
            import docx
            from django.core.files.storage import default_storage
            with default_storage.open(file_path, 'rb') as f:
                doc = docx.Document(f)
                text = [p.text for p in doc.paragraphs if p.text.strip()]
                for table in doc.tables:
                    for row in table.rows:
                        text.append(' | '.join(c.text for c in row.cells))
                return '\n'.join(text)
        except ImportError:
            return "DOCX文件（需安装python-docx）"
        except Exception as e:
            return f"DOCX提取失败: {e}"
