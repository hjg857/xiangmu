"""
报告AI建议生成服务
负责调用DeepSeek生成各个维度的评估建议
"""
import logging
from typing import Dict, List, Any
from apps.assessments.llm_service import LLMService

logger = logging.getLogger(__name__)


class ReportAIService:
    """报告AI建议生成服务"""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    def generate_all_suggestions(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """
        生成所有维度的AI建议
        :param report_data: 报告数据
        :return: 包含所有建议的字典
        """
        logger.info("开始生成AI评估建议")
        
        suggestions = {}
        
        # 1. 生成整体评估建议
        suggestions['overall'] = self.generate_overall_suggestion(report_data)
        
        # 2. 生成数据素养建议
        suggestions['literacy'] = self.generate_literacy_suggestion(report_data)
        
        # 3. 生成数据制度建议
        suggestions['institution'] = self.generate_institution_suggestion(report_data)
        
        # 4. 生成数据行为建议
        suggestions['behavior'] = self.generate_behavior_suggestion(report_data)
        
        # 5. 生成数据资产建议
        suggestions['asset'] = self.generate_asset_suggestion(report_data)
        
        # 6. 生成数据技术建议
        suggestions['technology'] = self.generate_technology_suggestion(report_data)
        
        logger.info("AI评估建议生成完成")
        return suggestions
    
    def generate_overall_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成整体评估建议"""
        # 1. 提取核心分值
        total_score = report_data['total_score']
        maturity_level = report_data['maturity_level']
        sec = report_data.get('secondary_scores', {})

        # 2. 提取细分维度得分（5分制）
        # A 数据素养
        a1, a2, a3 = sec.get('A1', 0), sec.get('A2', 0), sec.get('A3', 0)
        # B 数据制度
        b1, b2, b3 = sec.get('B1', 0), sec.get('B2', 0), sec.get('B3', 0)
        # C 数据行为
        c1, c2 = sec.get('C1', 0), sec.get('C2', 0)
        # D 数据资产
        d1, d2 = sec.get('D1', 0), sec.get('D2', 0)
        # E 数据技术
        e1, e2 = sec.get('E1', 0), sec.get('E2', 0)
        
        # 构建提示词
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：
        学校所获的分值：
        该校的整体数据文化得分为{total_score:.2f}分，所处等级为{maturity_level}。
        每个维度的得分是：
        数据素养：管理者数据素养（{a2:.2f}分）、教师数据素养（{a1:.2f}分）、学生数据素养（{a3:.2f}分）
        数据制度：数据组织机构（{b1:.2f}分）、数据人员配备（{b2:.2f}分）、数据管理文件（{b3:.2f}分）
        数据行为：数据行为监测（{c1:.2f}分）、数据应用成效（{c2:.2f}分）、
        数据资产：数据资产意识（{d1:.2f}分）、数据资产积累（{d2:.2f}分）、
        数据技术：数据基础设施（{e1:.2f}分）、数据安保能力（{e2:.2f}分）

        你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
        1.评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
        2.在建议中，表现较为优秀[3.0~4.0]分数段，表现非常优秀[4.0~5.0]分数段；这两个分数段不需要回复“应……（给出符合中小学校的可操作的建议）”。只呈现“表现……（根据四个分数区间匹配）”。（分数区间的判断必须要准确无误）
        3.必须按照我给的格式进行回复，不呈现分值，字数130字左右。
        该校数据文化处于……（等级），整体……（正面评价），但部分维度的表现……（提到一些不足）。（断行）
        其中，数据素养在管理者数据素养表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）；在教师数据素养表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）；在学生数据素养表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）。（断行）
        数据制度在数据组织机构表现……，应……（给出符合中小学校的可操作的建议）；在数据组织配备表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）；在数据管理文件表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）。（断行）
        数据行为在数据行为监测表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）；在数据应用成效表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）。（断行）
        数据资产在数据资产意识表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）；在数据资产积累表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）。（断行）
        数据技术在数据基础设施表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）。在数据安保能力表现……（根据四个分数区间匹配），应……（给出符合中小学校的可操作的建议）。
        """
        
        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成整体建议失败: {str(e)}")
            return self._get_default_overall_suggestion(total_score, maturity_level)

    def generate_literacy_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据素养建议"""
        """生成数据素养建议"""
        dimension_score = report_data['dimension_scores']['literacy']
        secondary_scores = report_data.get('secondary_scores', {})
        # 获取观测点分数（具体到意识、技能等），通常存在 observation_scores 中
        obs = report_data.get('observation_scores', {})

        # 核心修改：将真正的分值填入提示词，替换掉原来的 (X分)
        # 我们使用 5 分制传入，因为下方提示词定义的等级（0-1.5等）是基于 5 分制的
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：
        学校所获的分值：
        该校的数据素养得分为{dimension_score:.2f}分。每个维度的得分是：
        管理者数据素养：管理者数据意识与思维（{obs.get('A21', 0):.2f}分）、管理者数据知识与技能（{obs.get('A22', 0):.2f}分）、管理者数据评价与交流（{obs.get('A23', 0):.2f}分）、管理者数据应用与创新（{obs.get('A24', 0):.2f}分）、管理者数据伦理与隐私（{obs.get('A25', 0):.2f}分）
        教师数据素养：教师数据意识与思维（{obs.get('A11', 0):.2f}分）、教师数据知识与技能（{obs.get('A12', 0):.2f}分）、教师数据评价与交流（{obs.get('A13', 0):.2f}分）、教师数据应用与创新（{obs.get('A14', 0):.2f}分）、教师数据伦理与隐私（{obs.get('A15', 0):.2f}分）
        学生数据素养：学生数据意识与思维（{obs.get('A31', 0):.2f}分）、学生数据知识与技能（{obs.get('A32', 0):.2f}分）、学生数据评价与交流（{obs.get('A33', 0):.2f}分）、学生数据应用与创新（{obs.get('A34', 0):.2f}分）、学生数据伦理与隐私（{obs.get('A35', 0):.2f}分）

        你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
        1.评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
        2.在建议中，表现较为优秀[3.0~4.0]分数段，表现非常优秀[4.0~5.0]分数段；这两个分数段不需要回复“应……（给出符合中小学校的可操作的建议）”。只呈现“表现……（根据四个分数区间匹配）”。（分数区间的判断必须要准确无误）
        3.必须按照我给的格式进行回复，不呈现分值，字数110字左右。
        该校数据素养得分为{dimension_score:.2f}分，整体……（正面评价）。（断行）
        其中，管理者数据素养在管理者数据意识与思维表现……（根据四个分数区间匹配）；在管理者数据知识与技能表现……（根据四个分数区间匹配）；在管理者数据评价与交流表现……（根据四个分数区间匹配）；在管理者数据应用与创新表现……（根据四个分数区间匹配）；在管理者数据伦理与隐私表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        教师数据素养在教师数据意识与思维表现……（根据四个分数区间匹配）；在教师数据知识与技能表现……（根据四个分数区间匹配）；在教师数据评价与交流表现……（根据四个分数区间匹配）；在教师数据应用与创新表现……（根据四个分数区间匹配）；在教师数据伦理与隐私表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        学生数据素养在学生数据意识与思维表现……（根据四个分数区间匹配）；在学生数据知识与技能表现……（根据四个分数区间匹配）；在学生数据评价与交流表现……（根据四个分数区间匹配）；在学生数据应用与创新表现……（根据四个分数区间匹配）；在学生数据伦理与隐私表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。
        """

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据素养建议失败: {str(e)}")
            return self._get_default_dimension_suggestion(dimension_score, "数据素养")

    def generate_institution_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据制度建议"""
        dimension_score = report_data['dimension_scores']['institution']
        secondary_scores = report_data.get('secondary_scores', {})
        # 获取观测点具体分数（5分制）
        obs = report_data.get('observation_scores', {})

        # 核心修改：将真实的观测点分值（5分制）填入提示词，替换掉 (X分)
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：
        学校所获的分值：
        该校的数据制度得分为{dimension_score:.2f}分。每个维度的得分是：
        数据组织机构：数据领导/工作小组（{obs.get('B11', 0):.2f}分）、数据组织运行情况（{obs.get('B12', 0):.2f}分）
        数据人员配备：数据专职/兼职管理人员（{obs.get('B21', 0):.2f}分）、数据人员进修与培训情况（{obs.get('B22', 0):.2f}分）
        数据管理文件：数据管理制度类文件（{obs.get('B31', 0):.2f}分）、数据实践指导类文件（{obs.get('B32', 0):.2f}分）

        你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
        1.评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
        2.在建议中，表现较为优秀[3.0~4.0]分数段，表现非常优秀[4.0~5.0]分数段；这两个分数段不需要回复“应……（给出符合中小学校的可操作的建议）”。只呈现“表现……（根据四个分数区间匹配）”。（分数区间的判断必须要准确无误）
        3.必须按照我给的格式进行回复，不呈现分值，字数150字左右。
        该校数据制度得分为{dimension_score:.2f}分，整体……（正面评价）。（断行）
        其中，数据组织机构在数据领导/工作小组表现……（根据四个分数区间匹配）；在数据组织运行情况表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        数据人员配备在数据专职/兼职管理人员当中表现……（根据四个分数区间匹配）；在数据人员进修与培训情况当中表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        数据管理文件在数据管理制度类文件表现……（根据四个分数区间匹配）；在数据实践指导类文件表现……（根据四个分数区间匹配）应注重……（给出符合中小学校的可操作的建议）。
        """

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据制度建议失败: {str(e)}")
            return self._get_default_dimension_suggestion(dimension_score, "数据制度")

    def generate_behavior_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据行为建议"""
        dimension_score = report_data['dimension_scores']['behavior']
        # 获取具体的观测点分数（5分制）
        obs = report_data.get('observation_scores', {})

        # 核心修改：将真实的观测点分值填入提示词，替换掉 (X分)
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：
        学校所获的分值：
        该校的数据行为得分为{dimension_score:.2f}分。每个维度的得分是：
        数据行为监测：教师数据行为（{obs.get('C11', 0):.2f}分）、学生数据行为（{obs.get('C12', 0):.2f}分）、管理者数据行为（{obs.get('C13', 0):.2f}分）
        数据应用成效：数据应用特色成果（{obs.get('C21', 0):.2f}分）、数据应用社会影响（{obs.get('C22', 0):.2f}分）、应用效果主观评价（{obs.get('C23', 0):.2f}分）

        你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
        1.评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
        2.在建议中，表现较为优秀[3.0~4.0]分数段，表现非常优秀[4.0~5.0]分数段；这两个分数段不需要回复“应……（给出符合中小学校的可操作的建议）”。只呈现“表现……（根据四个分数区间匹配）”。（分数区间的判断必须要准确无误）
        3.必须按照我给的格式进行回复，不呈现分值，字数110字左右。
        该校数据行为得分为{dimension_score:.2f}分，整体……（正面评价）。（断行）
        其中，数据行为监测在教师数据行为表现……（根据四个分数区间匹配）；在学生数据行为表现……（根据四个分数区间匹配）；在管理者数据行为表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        数据应用成效在数据应用特色成果表现……（根据四个分数区间匹配）；在数据应用社会影响表现……（根据四个分数区间匹配）；在应用效果主观评价表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。
        """

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据行为建议失败: {str(e)}")
            return self._get_default_dimension_suggestion(dimension_score, "数据行为")

    def generate_asset_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据资产建议"""
        dimension_score = report_data['dimension_scores']['asset']
        # 获取具体的观测点分数（5分制）
        obs = report_data.get('observation_scores', {})

        # 核心修改：将真实的观测点分值填入提示词，替换掉 (X分)
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：
        学校所获的分值：
        该校的数据资产得分为{dimension_score:.2f}分。每个维度的得分是：
        数据资产意识：数据资产价值意识（{obs.get('D11', 0):.2f}分）、数据资产应用意识（{obs.get('D12', 0):.2f}分）、数据资产治理意识（{obs.get('D13', 0):.2f}分）
        数据资产积累：数据资产总量（{obs.get('D21', 0):.2f}分）、人均数据资产量（{obs.get('D22', 0):.2f}分）

        你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
        1.评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
        2.在建议中，表现较为优秀[3.0~4.0]分数段，表现非常优秀[4.0~5.0]分数段；这两个分数段不需要回复“应……（给出符合中小学校的可操作的建议）”。只呈现“表现……（根据四个分数区间匹配）”。（分数区间的判断必须要准确无误）
        3.必须按照我给的格式进行回复，不呈现分值，字数110字左右。
        该校数据资产得分为{dimension_score:.2f}分，整体……（正面评价）。（断行）
        其中，数据资产意识在数据资产价值意识表现……（根据四个分数区间匹配）；在数据资产应用意识表现……（根据四个分数区间匹配）；在数据资产治理意识表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        数据资产积累在数据资产总量表现……（根据四个分数区间匹配）；在人均数据资产量表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。
        """

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据资产建议失败: {str(e)}")
            return self._get_default_dimension_suggestion(dimension_score, "数据资产")

    def generate_technology_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据技术建议"""
        dimension_score = report_data['dimension_scores']['technology']
        # 获取具体的观测点分数（5分制）
        obs = report_data.get('observation_scores', {})

        # 核心修改：将真实的观测点分值（5分制）填入提示词，替换掉 (X分)
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：
        学校所获的分值：
        该校的数据技术得分为{dimension_score:.2f}分。每个维度的得分是：
        数据基础设施：数据硬件设施（{obs.get('E11', 0):.2f}分）、数据系统平台（{obs.get('E12', 0):.2f}分）
        数据安保水平：数据安全合规与认证（{obs.get('E21', 0):.2f}分）、数据风险事件记录（{obs.get('E22', 0):.2f}分）

        你需要根据分值所处的分段，再按照我给出的思路撰写建议内容：
        1.评价每个维度的四个分数区间分为：表现有待提升[大于0且小于等于1.5]分数段，表现比较良好[大于1.5且小于等于3.0]分数段，表现较为优秀[大于3.0且小于等于4.0]分数段，表现非常优秀[大于4.0且小于等于5.0]分数段。
        2.在建议中，表现较为优秀[3.0~4.0]分数段，表现非常优秀[4.0~5.0]分数段；这两个分数段不需要回复“应……（给出符合中小学校的可操作的建议）”。只呈现“表现……（根据四个分数区间匹配）”。（分数区间的判断必须要准确无误）
        3.必须按照我给的格式进行回复，不呈现分值，字数110字左右。
        该校数据技术得分为{dimension_score:.2f}分，整体……（正面评价）。（断行）
        其中数据基础设施在数据硬件设施表现……（根据四个分数区间匹配）；在数据系统平台表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。（断行）
        数据安保水平在：数据安全合规与认证表现……（根据四个分数区间匹配）；在数据风险事件记录表现……（根据四个分数区间匹配）；应注重……（给出符合中小学校的可操作的建议）。
        """


        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据技术建议失败: {str(e)}")
            return self._get_default_dimension_suggestion(dimension_score, "数据技术")
    
    def _get_default_overall_suggestion(self, total_score: float, maturity_level: str) -> str:
        """获取默认的整体建议（当AI调用失败时使用，基于5分制）"""
        # total_score 预期为 0.0 - 5.0 之间
        if total_score >= 4.0:
            return f"该校数据文化得分为{total_score:.2f}分，处于创新级，整体表现优秀，在数据素养、制度、行为、资产和技术等方面均有出色表现。建议继续保持并发挥引领作用，探索数字化转型的深度应用。"
        elif total_score >= 3.0:
            return f"该校数据文化得分为{total_score:.2f}分，处于成熟级，整体表现良好，已建立较完善的数据管理体系。建议进一步优化细节，向更高等级的创新应用迈进。"
        elif total_score >= 1.5:
            return f"该校数据文化得分为{total_score:.2f}分，处于成长级，已初步建立数据文化基础，但各维度发展尚不均衡。建议重点针对薄弱环节加强投入，提升整体数据治理水平。"
        else:
            return f"该校数据文化得分为{total_score:.2f}分，处于初始级，数据文化建设刚刚起步。建议从基础建设做起，逐步培养数据意识、完善管理制度、加强信息化基础保障。"

    def _get_default_dimension_suggestion(self, dimension_score: float, dimension_name: str) -> str:
        """获取默认的维度建议（当AI调用失败时使用，基于5分制）"""
        # 基于提示词标准：[0-1.5]较差，(1.5-4]均衡，(4-5]优秀
        if dimension_score > 4.0:
            return f"该校{dimension_name}维度表现优秀，得分为{dimension_score:.2f}分。建议总结优秀经验并在校内推广，维持高水平发展。"
        elif dimension_score > 1.5:
            return f"该校{dimension_name}维度表现均衡，得分为{dimension_score:.2f}分。虽然已具备一定基础，但在细节落实和深度应用上仍有提升空间，建议针对性加强建设。"
        else:
            return f"该校{dimension_name}维度目前表现较差，得分为{dimension_score:.2f}分。建议学校高度重视该维度的建设，从制度、人员或技术投入上寻找突破点，尽快补齐短板。"

