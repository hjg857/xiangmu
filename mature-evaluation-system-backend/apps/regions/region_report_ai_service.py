"""
区域报告 AI 建议生成服务
用于生成区域报告中的：
1. 初始级学校发展建议
2. 成长级学校发展建议
3. 成熟级学校发展建议
4. 引领级学校发展建议
5. 区域发展建议总述
6. 数据素养发展建议
7. 数据制度发展建议
8. 数据行为发展建议
9. 数据资产发展建议
10. 数据技术发展建议
11. 区域总体结论
"""

import logging
from typing import Dict, Any, List

from apps.assessments.llm_service import LLMService

logger = logging.getLogger(__name__)


class RegionReportAIService:
    """区域报告 AI 建议生成服务"""

    def __init__(self):
        self.llm_service = LLMService()

    def generate_all_suggestions(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成区域报告所有 AI 建议。
        每个建议单独调用一个函数，便于后续单独修改提示词。
        """
        logger.info("开始生成区域报告 AI 建议")

        result = {
            "level_suggestions": {
                "initial": self.generate_initial_level_suggestion(report_data),
                "growing": self.generate_growing_level_suggestion(report_data),
                "mature": self.generate_mature_level_suggestion(report_data),
                "leading": self.generate_leading_level_suggestion(report_data),
            },
            "development": {
                "summary": self.generate_development_summary(report_data),
                "items": [
                    self.generate_literacy_development_advice(report_data),
                    self.generate_institution_development_advice(report_data),
                    self.generate_behavior_development_advice(report_data),
                    self.generate_asset_development_advice(report_data),
                    self.generate_technology_development_advice(report_data),
                ],
                "conclusion": self.generate_development_conclusion(report_data),
            }
        }

        logger.info("区域报告 AI 建议生成完成")
        return result

    # 兼容你之前 view 里可能调用的旧方法名
    def generate_region_report_suggestions(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.generate_all_suggestions(report_data)

    # =========================
    # 一、各成熟度等级学校建议
    # =========================

    def generate_initial_level_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成初始级学校发展建议"""
        level = self._get_level_analysis(report_data, "initial")

        prompt = self._build_level_prompt(
            report_data=report_data,
            level_key="initial",
            level_name="初始级",
            level_data=level,
            focus="基础建设、数据制度、数据技术支撑和数据意识启蒙",
            style_hint="重点强调补基础、建机制、促启动，避免提出过高要求。"
        )

        return self._call_ai(
            prompt,
            self._default_level_suggestion("initial")
        )

    def generate_growing_level_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成成长级学校发展建议"""
        level = self._get_level_analysis(report_data, "growing")

        prompt = self._build_level_prompt(
            report_data=report_data,
            level_key="growing",
            level_name="成长级",
            level_data=level,
            focus="制度完善、应用场景拓展、数据行为常态化和薄弱维度补强",
            style_hint="重点强调从已有基础走向稳定运行，突出可持续改进。"
        )

        return self._call_ai(
            prompt,
            self._default_level_suggestion("growing")
        )

    def generate_mature_level_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成成熟级学校发展建议"""
        level = self._get_level_analysis(report_data, "mature")

        prompt = self._build_level_prompt(
            report_data=report_data,
            level_key="mature",
            level_name="成熟级",
            level_data=level,
            focus="高质量数据应用、成果沉淀、跨场景协同和经验推广",
            style_hint="重点强调巩固优势、形成特色、总结经验。"
        )

        return self._call_ai(
            prompt,
            self._default_level_suggestion("mature")
        )

    def generate_leading_level_suggestion(self, report_data: Dict[str, Any]) -> str:
        """生成引领级学校发展建议"""
        level = self._get_level_analysis(report_data, "leading")

        prompt = self._build_level_prompt(
            report_data=report_data,
            level_key="leading",
            level_name="引领级",
            level_data=level,
            focus="示范引领、区域带动、经验输出和创新应用",
            style_hint="重点强调示范辐射、经验复制和区域协同提升。"
        )

        return self._call_ai(
            prompt,
            self._default_level_suggestion("leading")
        )

    def _build_level_prompt(
        self,
        report_data: Dict[str, Any],
        level_key: str,
        level_name: str,
        level_data: Dict[str, Any],
        focus: str,
        style_hint: str
    ) -> str:
        region_name = self._region_name(report_data)
        weak_text = self._weak_dimensions_text(level_data.get("dimension_average", {}))

        count = level_data.get("count", 0)
        avg_score = self._score(level_data.get("avg_score"))

        dim = level_data.get("dimension_average", {})

        return f"""
你现在是一名中小学数据文化成熟度评估专家，需要为区域报告撰写“{level_name}学校分析”部分的发展建议。

【区域名称】
{region_name}

【学校等级】
{level_name}

【该等级学校数量】
{count} 所

【该等级平均得分】
{avg_score:.2f}

【该等级五维度平均分】
数据素养：{self._score(dim.get("literacy")):.2f}
数据制度：{self._score(dim.get("institution")):.2f}
数据行为：{self._score(dim.get("behavior")):.2f}
数据资产：{self._score(dim.get("asset")):.2f}
数据技术：{self._score(dim.get("technology")):.2f}

【主要薄弱维度】
{weak_text}

【建议重点】
{focus}

【写作要求】
1. 面向区域教育管理部门，不要写成单个学校报告。
2. 必须围绕“{level_name}学校”这一群体来写。
3. 建议要结合该等级学校的平均水平和薄弱维度。
4. 语言正式、自然、可操作。
5. 不要出现“根据你提供的数据”等口语化表达。
6. 不要编造具体学校名称。
7. 字数控制在 80 到 120 字。
8. {style_hint}

请直接输出建议正文，不要输出标题，不要输出编号。
"""

    # =========================
    # 二、区域发展建议总述
    # =========================

    def generate_development_summary(self, report_data: Dict[str, Any]) -> str:
        """生成区域发展建议开头总结"""
        summary = report_data.get("summary", {})
        dim = report_data.get("dimension_average", {})

        prompt = f"""
你现在是一名中小学数据文化成熟度评估专家，需要为区域报告撰写“区域发展建议”的开头总结。

【区域名称】
{self._region_name(report_data)}

【区域概况】
学校总数：{summary.get("school_count", 0)} 所
已完成评估学校数：{summary.get("completed_school_count", 0)} 所
区域平均分：{self._score(summary.get("avg_score")):.2f}
最高分：{self._score(summary.get("highest_score")):.2f}
最低分：{self._score(summary.get("lowest_score")):.2f}

【五维度平均分】
数据素养：{self._score(dim.get("literacy")):.2f}
数据制度：{self._score(dim.get("institution")):.2f}
数据行为：{self._score(dim.get("behavior")):.2f}
数据资产：{self._score(dim.get("asset")):.2f}
数据技术：{self._score(dim.get("technology")):.2f}

【主要短板】
{self._weak_dimensions_text(dim)}

【写作要求】
1. 面向区域教育管理部门。
2. 概括区域整体表现、优势和短板。
3. 不要写成单个学校报告。
4. 字数控制在 60 到 100 字。
5. 直接输出正文，不要标题。
"""

        return self._call_ai(
            prompt,
            self._default_development_summary(report_data)
        )

    # =========================
    # 三、五类区域发展建议
    # =========================

    def generate_literacy_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据素养发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="literacy",
            dimension_name="数据素养",
            title="加强数据素养培养",
            focus="管理者、教师和学生的数据意识、数据知识、数据应用能力、数据伦理与隐私保护",
            requirement="建议重点围绕分层培训、教师数据应用能力提升、学生数据意识培养和管理者数据决策能力建设展开。"
        )

        return {
            "index": 1,
            "title": "加强数据素养培养",
            "dimension": "数据素养",
            "content": content
        }

    def generate_institution_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据制度发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="institution",
            dimension_name="数据制度",
            title="完善数据治理制度",
            focus="数据组织机构、数据人员配备、数据管理文件、职责分工和制度运行机制",
            requirement="建议重点围绕区域统一规范、学校数据职责、制度文件建设和数据治理运行机制展开。"
        )

        return {
            "index": 2,
            "title": "完善数据治理制度",
            "dimension": "数据制度",
            "content": content
        }

    def generate_behavior_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据行为发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="behavior",
            dimension_name="数据行为",
            title="推动数据应用落地",
            focus="教师数据行为、学生数据行为、管理者数据行为、数据应用成果和应用成效",
            requirement="建议重点围绕教学改进、学生发展分析、管理决策、资源配置和数据应用场景常态化展开。"
        )

        return {
            "index": 3,
            "title": "推动数据应用落地",
            "dimension": "数据行为",
            "content": content
        }

    def generate_asset_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据资产发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="asset",
            dimension_name="数据资产",
            title="提升数据资产意识",
            focus="数据资产价值意识、应用意识、治理意识、数据资源积累和数据复用",
            requirement="建议重点围绕数据资源目录、数据质量管理、数据共享机制和数据资产价值转化展开。"
        )

        return {
            "index": 4,
            "title": "提升数据资产意识",
            "dimension": "数据资产",
            "content": content
        }

    def generate_technology_development_advice(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据技术发展建议"""
        content = self._generate_dimension_development_content(
            report_data=report_data,
            dimension_key="technology",
            dimension_name="数据技术",
            title="夯实数据技术支撑",
            focus="数据硬件设施、数据系统平台、数据安全合规、终端配置和基础设施保障",
            requirement="建议重点围绕数据平台建设、数字终端配置、数据安全保障和基础设施持续运维展开。"
        )

        return {
            "index": 5,
            "title": "夯实数据技术支撑",
            "dimension": "数据技术",
            "content": content
        }

    def _generate_dimension_development_content(
        self,
        report_data: Dict[str, Any],
        dimension_key: str,
        dimension_name: str,
        title: str,
        focus: str,
        requirement: str
    ) -> str:
        dim = report_data.get("dimension_average", {})
        score = self._score(dim.get(dimension_key))
        region_name = self._region_name(report_data)

        prompt = f"""
你现在是一名中小学数据文化成熟度评估专家，需要为区域报告撰写一条发展建议。

【区域名称】
{region_name}

【建议标题】
{title}

【关联维度】
{dimension_name}

【该维度区域平均分】
{score:.2f}

【该维度关注内容】
{focus}

【写作要求】
1. 面向区域教育管理部门，不要写成单个学校报告。
2. 建议要体现区域层面的统筹、指导、推进和保障。
3. 内容要可操作，避免空泛表述。
4. 不要出现“根据你提供的数据”等口语化表达。
5. 不要编造具体学校名称。
6. 字数控制在 80 到 120 字。
7. {requirement}

请直接输出建议正文，不要输出标题，不要编号。
"""

        return self._call_ai(
            prompt,
            self._default_dimension_advice(dimension_key)
        )

    # =========================
    # 四、总体结论
    # =========================

    def generate_development_conclusion(self, report_data: Dict[str, Any]) -> str:
        """生成区域总体结论"""
        summary = report_data.get("summary", {})
        dim = report_data.get("dimension_average", {})

        prompt = f"""
你现在是一名中小学数据文化成熟度评估专家，需要为区域报告撰写最终的“总体结论”。

【区域名称】
{self._region_name(report_data)}

【区域平均分】
{self._score(summary.get("avg_score")):.2f}

【五维度平均分】
数据素养：{self._score(dim.get("literacy")):.2f}
数据制度：{self._score(dim.get("institution")):.2f}
数据行为：{self._score(dim.get("behavior")):.2f}
数据资产：{self._score(dim.get("asset")):.2f}
数据技术：{self._score(dim.get("technology")):.2f}

【主要短板】
{self._weak_dimensions_text(dim)}

【写作要求】
1. 用于区域报告结尾。
2. 总结区域整体建设水平、后续改进方向和管理建议。
3. 语言正式、简洁、有总结性。
4. 不要写成单个学校报告。
5. 字数控制在 80 到 120 字。
6. 直接输出正文，不要标题。
"""

        return self._call_ai(
            prompt,
            self._default_conclusion()
        )

    # =========================
    # 五、通用工具函数
    # =========================

    def _call_ai(self, prompt: str, default_text: str) -> str:
        """统一调用大模型，失败时返回默认文本"""
        try:
            result = self.llm_service._call_api(prompt)
            result = str(result or "").strip()

            if not result:
                return default_text

            # 防止模型返回 Markdown 包裹
            result = result.replace("```text", "").replace("```", "").strip()
            return result

        except Exception as e:
            logger.error(f"区域报告 AI 建议生成失败: {str(e)}")
            return default_text

    def _region_name(self, report_data: Dict[str, Any]) -> str:
        region = report_data.get("region", {}) or {}
        return f"{region.get('province', '')}{region.get('city', '')}{region.get('name', '')}" or "当前区域"

    def _score(self, value: Any) -> float:
        try:
            if value is None or value == "":
                return 0.0
            return float(value)
        except Exception:
            return 0.0

    def _get_level_analysis(self, report_data: Dict[str, Any], level_key: str) -> Dict[str, Any]:
        levels = report_data.get("level_analysis", []) or []
        for item in levels:
            if item.get("key") == level_key:
                return item

        return {
            "key": level_key,
            "count": 0,
            "avg_score": 0,
            "dimension_average": {}
        }

    def _weak_dimensions_text(self, dimension_average: Dict[str, Any]) -> str:
        weak = self._weak_dimensions(dimension_average)
        if not weak:
            return "暂无明显短板"

        return "、".join([item["label"] for item in weak[:2]])

    def _weak_dimensions(self, dimension_average: Dict[str, Any]) -> List[Dict[str, Any]]:
        label_map = {
            "literacy": "数据素养",
            "institution": "数据制度",
            "behavior": "数据行为",
            "asset": "数据资产",
            "technology": "数据技术",
        }

        result = []
        for key, label in label_map.items():
            result.append({
                "key": key,
                "label": label,
                "score": self._score(dimension_average.get(key))
            })

        result.sort(key=lambda x: x["score"])
        return result

    # =========================
    # 六、默认兜底文本
    # =========================

    def _default_level_suggestion(self, level_key: str) -> str:
        defaults = {
            "initial": "该等级学校整体处于基础建设阶段，应优先完善数据制度、基础平台和数据采集机制，逐步提升师生数据意识与常态化应用能力，为后续数据文化建设奠定基础。",
            "growing": "该等级学校已具备一定数据文化基础，但各维度发展仍不均衡。建议围绕薄弱维度开展专项提升，推动数据应用从零散实践走向稳定运行。",
            "mature": "该等级学校整体发展较为成熟，建议进一步加强跨场景数据应用、成果沉淀和经验总结，形成可复制、可推广的区域示范样板。",
            "leading": "该等级学校具备较好的引领基础，建议发挥示范带动作用，输出制度经验、应用案例和治理方法，带动区域内其他学校共同提升。"
        }
        return defaults.get(level_key, "暂无建议。")

    def _default_development_summary(self, report_data: Dict[str, Any]) -> str:
        dim = report_data.get("dimension_average", {})
        weak = self._weak_dimensions_text(dim)
        return f"从区域整体表现看，当前短板主要集中在{weak}等方面，应围绕薄弱维度开展分类指导，并推动高水平学校发挥示范带动作用。"

    def _default_dimension_advice(self, dimension_key: str) -> str:
        defaults = {
            "literacy": "建议面向管理者、教师和学生开展分层培训，提升数据意识、数据分析能力和数据伦理素养，推动数据素养培养融入日常教学与管理过程。",
            "institution": "建议完善区域数据治理规范，推动学校明确数据职责分工、制度文件和常态化运行机制，提升学校数据管理的规范化水平。",
            "behavior": "建议围绕教学改进、学生发展和管理决策等场景，推动数据应用从零散使用走向稳定实践，形成可持续的数据应用机制。",
            "asset": "建议建立数据资源目录，强化数据质量、共享和复用机制，提升学校数据资产沉淀能力，促进数据资源向教育治理价值转化。",
            "technology": "建议完善数据平台、终端设备和安全保障体系，加强数据系统运维和安全合规管理，为区域数据文化建设提供稳定技术支撑。"
        }
        return defaults.get(dimension_key, "建议结合区域实际情况，围绕薄弱环节开展分类指导和持续改进。")

    def _default_conclusion(self) -> str:
        return "区域后续应坚持分类指导、重点突破和示范带动相结合，针对低分维度开展专项改进，同时总结高分学校经验，推动区域整体数据文化水平持续提升。"