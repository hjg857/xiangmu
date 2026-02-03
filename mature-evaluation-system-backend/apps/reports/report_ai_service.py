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
        total_score = report_data['total_score']
        maturity_level = report_data['maturity_level']
        dimension_scores = report_data['dimension_scores']
        secondary_scores = report_data.get('secondary_scores', {})
        
        # 构建提示词
        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：

该校的整体数据文化得分为{total_score:.2f}分，所处等级为{maturity_level}。

等级分数划分为：初始级（0~70）成长级（70~80）、成熟级（80~90）、引领级（90~100）

每个维度评价的分数分为：
表现较差[0-60]分数段，表现均衡[60-80]分数段，表现优秀[80-100]分数段。

每个维度的得分是：
数据素养：{dimension_scores['literacy']:.2f}分
数据制度：{dimension_scores['institution']:.2f}分
数据行为：{dimension_scores['behavior']:.2f}分
数据资产：{dimension_scores['asset']:.2f}分
数据技术：{dimension_scores['technology']:.2f}分

你需要按照我给出的思路撰写建议内容：
1.字数150字左右
2.必须按照我给的格式进行回复，不呈现分值：

该校数据文化处于……（等级），整体……（正面评价），但每个维度的表现……（提到一些不足）。

数据素养在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。数据制度在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。数据行为在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。数据资产在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。数据技术在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。
"""
        
        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成整体建议失败: {str(e)}")
            return self._get_default_overall_suggestion(total_score, maturity_level)
    
    def generate_literacy_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成数据素养建议"""
        dimension_score = report_data['dimension_scores']['literacy']
        secondary_scores = report_data.get('secondary_scores', {})

        a1_score = secondary_scores.get('A1', 0) * 20  # 转换为100分制
        a2_score = secondary_scores.get('A2', 0) * 20
        a3_score = secondary_scores.get('A3', 0) * 20

        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：

该校的数据素养维度得分为{dimension_score:.2f}分。

二级指标得分：
- 教师数据素养（A1）：{a1_score:.2f}分
- 管理者数据素养（A2）：{a2_score:.2f}分
- 学生数据素养（A3）：{a3_score:.2f}分

每个二级指标评价的分数分为：
表现较差[0-60]分数段，表现均衡[60-80]分数段，表现优秀[80-100]分数段。

你需要按照我给出的思路撰写建议内容：
1.字数150字左右
2.必须按照我给的格式进行回复，不呈现分值：

该校数据素养维度得分……（正面评价），但各二级指标表现……（提到一些不足）。

教师数据素养在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。管理者数据素养在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。学生数据素养在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。
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

        b1_score = secondary_scores.get('B1', 0) * 20
        b2_score = secondary_scores.get('B2', 0) * 20
        b3_score = secondary_scores.get('B3', 0) * 20

        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：

该校的数据制度维度得分为{dimension_score:.2f}分。

二级指标得分：
- 数据组织机构（B1）：{b1_score:.2f}分
- 数据人员配备（B2）：{b2_score:.2f}分
- 数据管理文件（B3）：{b3_score:.2f}分

每个二级指标评价的分数分为：
表现较差[0-60]分数段，表现均衡[60-80]分数段，表现优秀[80-100]分数段。

你需要按照我给出的思路撰写建议内容：
1.字数150字左右
2.必须按照我给的格式进行回复，不呈现分值：

该校数据制度维度得分……（正面评价），但各二级指标表现……（提到一些不足）。

数据组织机构在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。数据人员配备在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。数据管理文件在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。
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
        secondary_scores = report_data.get('secondary_scores', {})

        c1_score = secondary_scores.get('C1', 0) * 20
        c2_score = secondary_scores.get('C2', 0) * 20

        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：

该校的数据行为维度得分为{dimension_score:.2f}分。

二级指标得分：
- 数据行为监测（C1）：{c1_score:.2f}分
- 数据应用成效（C2）：{c2_score:.2f}分

每个二级指标评价的分数分为：
表现较差[0-60]分数段，表现均衡[60-80]分数段，表现优秀[80-100]分数段。

你需要按照我给出的思路撰写建议内容：
1.字数150字左右
2.必须按照我给的格式进行回复，不呈现分值：

该校数据行为维度得分……（正面评价），但各二级指标表现……（提到一些不足）。

数据行为监测在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。数据应用成效在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。
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
        secondary_scores = report_data.get('secondary_scores', {})

        d1_score = secondary_scores.get('D1', 0) * 20
        d2_score = secondary_scores.get('D2', 0) * 20

        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：

该校的数据资产维度得分为{dimension_score:.2f}分。

二级指标得分：
- 数据资产意识（D1）：{d1_score:.2f}分
- 数据资产积累（D2）：{d2_score:.2f}分

每个二级指标评价的分数分为：
表现较差[0-60]分数段，表现均衡[60-80]分数段，表现优秀[80-100]分数段。

你需要按照我给出的思路撰写建议内容：
1.字数150字左右
2.必须按照我给的格式进行回复，不呈现分值：

该校数据资产维度得分……（正面评价），但各二级指标表现……（提到一些不足）。

数据资产意识在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。数据资产积累在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。
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
        secondary_scores = report_data.get('secondary_scores', {})

        e1_score = secondary_scores.get('E1', 0) * 20
        e2_score = secondary_scores.get('E2', 0) * 20

        prompt = f"""你好，现在我要进行一项面向中小学校的数据文化评价，需要你结合学校所获的分值，根据分值所处的分段，给出对应的建议：

该校的数据技术维度得分为{dimension_score:.2f}分。

二级指标得分：
- 数据基础设施（E1）：{e1_score:.2f}分
- 数据安保水平（E2）：{e2_score:.2f}分

每个二级指标评价的分数分为：
表现较差[0-60]分数段，表现均衡[60-80]分数段，表现优秀[80-100]分数段。

你需要按照我给出的思路撰写建议内容：
1.字数150字左右
2.必须按照我给的格式进行回复，不呈现分值：

该校数据技术维度得分……（正面评价），但各二级指标表现……（提到一些不足）。

数据基础设施在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。数据安保水平在……表现较差，应……（给出符合中小学校的可操作的建议），在……表现均衡，在……表现优秀。
"""

        try:
            result = self.llm_service._call_api(prompt)
            return result
        except Exception as e:
            logger.error(f"生成数据技术建议失败: {str(e)}")
            return self._get_default_dimension_suggestion(dimension_score, "数据技术")
    
    def _get_default_overall_suggestion(self, total_score: float, maturity_level: str) -> str:
        """获取默认的整体建议（当AI调用失败时使用）"""
        if total_score >= 90:
            return "该校数据文化处于引领级，整体表现优秀，在数据素养、制度、行为、资产和技术等方面均有出色表现。建议继续保持并分享经验，发挥示范引领作用。"
        elif total_score >= 80:
            return "该校数据文化处于成熟级，整体表现良好，但仍有提升空间。建议在薄弱环节加强建设，进一步完善数据文化体系。"
        elif total_score >= 70:
            return "该校数据文化处于成长级，已初步建立数据文化基础，但各维度发展不均衡。建议重点加强薄弱环节，提升整体数据文化水平。"
        else:
            return "该校数据文化处于初始级，数据文化建设刚刚起步。建议从基础做起，逐步建立数据意识、完善制度、加强培训，夯实数据文化基础。"

    def _get_default_dimension_suggestion(self, dimension_score: float, dimension_name: str) -> str:
        """获取默认的维度建议（当AI调用失败时使用）"""
        if dimension_score >= 80:
            return f"该校{dimension_name}维度表现优秀，建议继续保持并进一步提升。"
        elif dimension_score >= 60:
            return f"该校{dimension_name}维度表现均衡，建议在薄弱环节加强建设。"
        else:
            return f"该校{dimension_name}维度表现较差，建议重点加强该维度的建设，提升整体水平。"

