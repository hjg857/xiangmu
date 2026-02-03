"""
计分配置文件
所有计分规则集中管理，便于后续调整
"""

# ==================== 数据素养维度 (A) ====================

# 问卷题目范围和满分配置
LITERACY_SURVEY_CONFIG = {
    'teacher': {
        'A11': {'range': (6, 13), 'max_score': 40, 'name': '教师数据意识与思维'},
        'A12': {'range': (14, 20), 'max_score': 35, 'name': '教师数据知识与技能'},
        'A13': {'range': (21, 23), 'max_score': 15, 'name': '教师数据评价与交流'},
        'A14': {'range': (24, 31), 'max_score': 40, 'name': '教师数据应用与创新'},
        'A15': {'range': (32, 34), 'max_score': 15, 'name': '教师数据伦理与隐私'},
    },
    'manager': {
        'A21': {'range': (7, 14), 'max_score': 40, 'name': '管理者数据意识与思维'},
        'A22': {'range': (15, 22), 'max_score': 40, 'name': '管理者数据知识与技能'},
        'A23': {'range': (23, 25), 'max_score': 15, 'name': '管理者数据评价与交流'},
        'A24': {'range': (26, 33), 'max_score': 40, 'name': '管理者数据应用与创新'},
        'A25': {'range': (34, 37), 'max_score': 20, 'name': '管理者数据伦理与隐私'},
    },
    'student': {
        'A31': {'range': (4, 10), 'max_score': 35, 'name': '学生数据意识与思维'},
        'A32': {'range': (11, 17), 'max_score': 35, 'name': '学生数据知识与技能'},
        'A33': {'range': (18, 19), 'max_score': 10, 'name': '学生数据评价与交流'},
        'A34': {'range': (20, 25), 'max_score': 30, 'name': '学生数据应用与创新'},
        'A35': {'range': (26, 28), 'max_score': 15, 'name': '学生数据伦理与隐私'},
    }
}

# 5点量表计分规则
SCALE_SCORE_MAPPING = {
    'A': 1, '非常不符合': 1,
    'B': 2, '不符合': 2,
    'C': 3, '一般': 3,
    'D': 4, '符合': 4,
    'E': 5, '非常符合': 5
}


# ==================== 数据制度维度 (B) ====================

INSTITUTION_SCORING_RULES = {
    # B1 数据组织机构
    'B11': {
        'name': '数据领导/工作小组',
        'field': 'has_leadership_group',
        'max_score': 10,
        'rules': {
            True: 10,
            False: 0
        }
    },
    'B12': {
        'name': '数据组织运行情况',
        'field': 'meeting_activity_count',
        'max_score': 10,
        'rules': [
            {'condition': 'lt', 'value': 5, 'score': 3},
            {'condition': 'between', 'min': 5, 'max': 15, 'score': 6},
            {'condition': 'gt', 'value': 15, 'score': 10}
        ]
    },
    
    # B2 数据人员配备
    'B21': {
        'name': '数据专职/兼职管理人员',
        'max_score': 20,
        'sub_items': [
            {
                'field': 'has_data_staff',
                'type': 'boolean',
                'rules': {True: 'continue', False: 0}  # False则整个B21为0分
            },
            {
                'field': 'staff_count',
                'type': 'staff_count',
                'max_score': 10,
                'rules': {
                    'fulltime': 5,  # 每名专职5分
                    'parttime': 3   # 每名兼职3分
                }
            },
            {
                'field': 'has_clear_responsibilities',
                'type': 'boolean',
                'rules': {True: 10, False: 0}
            }
        ]
    },
    'B22': {
        'name': '数据人员进修与培训情况',
        'max_score': 30,
        'sub_items': [
            {
                'field': 'has_training',
                'type': 'boolean',
                'rules': {True: 'continue', False: 0}  # False则整个B22为0分
            },
            {
                'field': 'training_count',
                'type': 'range',
                'max_score': 10,
                'rules': [
                    {'condition': 'lt', 'value': 5, 'score': 3},
                    {'condition': 'between', 'min': 5, 'max': 15, 'score': 6},
                    {'condition': 'gt', 'value': 15, 'score': 10}
                ]
            },
            {
                'field': 'certificates',
                'type': 'certificates',
                'max_score': 20,
                'rules': {
                    'national': 5,
                    'provincial': 3,
                    'city': 1
                }
            }
        ]
    },
    
    # B3 数据管理文件
    'B31': {
        'name': '数据管理制度类文件',
        'max_score': 40,
        'sub_items': [
            {
                'field': 'has_management_doc',
                'type': 'boolean',
                'rules': {True: 'continue', False: 0}
            },
            {
                'field': 'management_doc_count_total',
                'type': 'doc_count',
                'max_score': 20,
                'score_per_doc': 5
            },
            {
                'field': 'management_doc_files',
                'type': 'llm_quality',
                'max_score': 20,
                'llm_prompt': '请从规范性、专业性、完整性、特色化四个维度分析该数据管理制度文件的整体质量，给出0-20分的评分。'
            }
        ]
    },
    'B32': {
        'name': '数据实践指导类文件',
        'max_score': 40,
        'sub_items': [
            {
                'field': 'has_practice_doc',
                'type': 'boolean',
                'rules': {True: 'continue', False: 0}
            },
            {
                'field': 'practice_doc_count_total',
                'type': 'doc_count',
                'max_score': 20,
                'score_per_doc': 5
            },
            {
                'field': 'practice_doc_files',
                'type': 'llm_quality',
                'max_score': 20,
                'llm_prompt': '请从规范性、完整性、可操作性、实用性四个维度分析该数据实践指导文件的整体质量，给出0-20分的评分。'
            }
        ]
    }
}


# ==================== 数据行为维度 (C) ====================

BEHAVIOR_SCORING_RULES = {
    # C1 数据行为监测
    'C11': {
        'name': '教师数据行为',
        'field': 'teacher_login_freq',
        'max_score': 10,
        'rules': [
            {'condition': 'lt', 'value': 100, 'score': 3},
            {'condition': 'between', 'min': 100, 'max': 200, 'score': 6},
            {'condition': 'gt', 'value': 200, 'score': 10}
        ]
    },
    'C12': {
        'name': '学生数据行为',
        'field': 'student_login_freq',
        'max_score': 10,
        'rules': [
            {'condition': 'lt', 'value': 50, 'score': 3},
            {'condition': 'between', 'min': 50, 'max': 100, 'score': 6},
            {'condition': 'gt', 'value': 100, 'score': 10}
        ]
    },
    'C13': {
        'name': '管理者数据行为',
        'field': 'manager_login_freq',
        'max_score': 10,
        'rules': [
            {'condition': 'lt', 'value': 100, 'score': 3},
            {'condition': 'between', 'min': 100, 'max': 200, 'score': 6},
            {'condition': 'gt', 'value': 200, 'score': 10}
        ]
    },
    
    # C2 数据应用成效
    'C21': {
        'name': '数据应用特色成果',
        'max_score': 60,
        'sub_items': [
            {
                'name': '公开发表成果',
                'max_score': 20,
                'fields': {
                    'published_paper_count': 3,  # 每篇论文3分
                    'published_book_count': 6    # 每部著作6分
                }
            },
            {
                'name': '入选优秀案例',
                'max_score': 20,
                'fields': {
                    'case_national_count': 5,
                    'case_provincial_count': 3,
                    'case_city_count': 1
                }
            },
            {
                'name': '荣誉奖励',
                'max_score': 20,
                'fields': {
                    'award_national_count': 5,
                    'award_provincial_count': 3,
                    'award_city_count': 1
                }
            }
        ]
    },
    'C22': {
        'name': '数据应用社会影响',
        'max_score': 50,
        'sub_items': [
            {
                'name': '媒体宣传报道',
                'max_score': 20,
                'fields': {
                    'media_national_count': 5,
                    'media_provincial_count': 3,
                    'media_city_count': 1
                }
            },
            {
                'name': '会议交流分享',
                'max_score': 20,
                'fields': {
                    'conference_national_count': 5,
                    'conference_provincial_count': 3,
                    'conference_city_count': 1
                }
            },
            {
                'name': '参观学习',
                'field': 'visit_count',
                'max_score': 10,
                'score_per_visit': 2
            }
        ]
    },
    'C23': {
        'name': '应用效果主观评价',
        'type': 'survey',
        'max_score': 85,
        'survey_ranges': {
            'teacher': (35, 40),   # 教师问卷35-40题
            'student': (29, 34),   # 学生问卷29-34题
            'manager': (52, 56)    # 管理者问卷52-56题
        }
    }
}


# ==================== 数据资产维度 (D) ====================

ASSET_SCORING_RULES = {
    # D1 数据资产意识
    'D11': {
        'name': '数据资产价值意识',
        'type': 'survey',
        'max_score': 20,
        'survey_range': (38, 41),  # 管理者问卷38-41题
        'survey_type': 'manager'
    },
    'D12': {
        'name': '数据资产应用意识',
        'type': 'survey',
        'max_score': 20,
        'survey_range': (42, 45),  # 管理者问卷42-45题
        'survey_type': 'manager'
    },
    'D13': {
        'name': '数据资产治理意识',
        'type': 'survey',
        'max_score': 30,
        'survey_range': (46, 51),  # 管理者问卷46-51题
        'survey_type': 'manager'
    },
    
    # D2 数据资产积累
    'D21': {
        'name': '数据资产总量',
        'field': 'total_data_volume',  # 需要计算总量
        'max_score': 10,
        'rules': [
            {'condition': 'lte', 'value': 10000, 'score': 2},
            {'condition': 'between', 'min': 10000, 'max': 55000, 'score': 4},
            {'condition': 'between', 'min': 55000, 'max': 90000, 'score': 6},
            {'condition': 'gt', 'value': 90000, 'score': 10}
        ]
    },
}


# ==================== 数据技术维度 (E) ====================

TECHNOLOGY_SCORING_RULES = {
    # E1 数据基础设施
    'E11': {
        'name': '数据硬件设施',
        'max_score': 30,
        'sub_items': [
            {
                'name': '数据中心标准',
                'field': 'data_center_standard',
                'max_score': 10,
                'rules': {
                    'fully_compliant': 10,
                    'partially_compliant': 6,
                    'not_compliant': 3
                }
            },
            {
                'name': '生机比',
                'field': 'student_device_ratio',
                'max_score': 10,
                'rules': {
                    'high': 3,    # >15:1
                    'medium': 6,  # 15:1~6:1
                    'low': 10     # <6:1
                }
            },
            {
                'name': '师机比',
                'field': 'teacher_device_ratio',
                'max_score': 10,
                'rules': {
                    'high': 3,    # >4:1
                    'medium': 6,  # 1:1~4:1
                    'low': 10     # <1:1
                }
            }
        ]
    },
    'E12': {
        'name': '数据系统平台',
        'field': 'has_data_platform',
        'max_score': 10,
        'rules': {
            True: 10,
            False: 0
        }
    },
    'E13': {
        'name': '专享云服务完全满足需求',
        'max_score': 10,
        'rules': {
            'fully_meets': 10,
            'partially_meets': 6,
            'not_meets': 3
        }
    },
    
    # E2 数据安保水平
    'E21': {
        'name': '数据安全合规与认证',
        'max_score': 20,
        'sub_items': [
            {
                'name': '安保认证数量',
                'field': 'security_certified_count',
                'max_score': 10,
                'rules': [
                    {'condition': 'between', 'min': 1, 'max': 2, 'score': 3},
                    {'condition': 'between', 'min': 3, 'max': 4, 'score': 6},
                    {'condition': 'gte', 'value': 5, 'score': 10}
                ]
            },
            {
                'name': '安保认证比例',
                'field': 'security_certified_ratio',
                'max_score': 10,
                'rules': {
                    'low': 3,
                    'medium': 6,
                    'high': 10
                }
            }
        ]
    },
    'E22': {
        'name': '数据风险事件记录',
        'field': 'has_security_incident',
        'max_score': 0,  # 这是扣分项
        'rules': {
            True: -10,   # 发生过扣10分
            False: 0     # 未发生不扣分
        }
    }
}


# ==================== 维度权重配置 ====================

# 一级指标权重（五个维度）
DIMENSION_WEIGHTS = {
    'A': 0.3543,  # 数据素养
    'B': 0.1578,  # 数据制度
    'C': 0.1930,  # 数据行为
    'D': 0.1549,  # 数据资产
    'E': 0.1400   # 数据技术
}

# 二级指标权重（在各自一级指标内的权重）
SECONDARY_WEIGHTS = {
    # A 数据素养
    'A1': 0.3748,  # 教师数据素养
    'A2': 0.3443,  # 管理者数据素养
    'A3': 0.2809,  # 学生数据素养

    # B 数据制度
    'B1': 0.3599,  # 数据组织机构
    'B2': 0.4131,  # 数据人员配备
    'B3': 0.2270,  # 数据管理文件

    # C 数据行为
    'C1': 0.4679,  # 数据行为监测
    'C2': 0.5321,  # 数据应用成效

    # D 数据资产
    'D1': 0.4795,  # 数据资产意识
    'D2': 0.5205,  # 数据资产积累

    # E 数据技术
    'E1': 0.5449,  # 数据基础设施
    'E2': 0.4551   # 数据安保水平
}

# 观测点权重（在各自二级指标内的权重）
OBSERVATION_WEIGHTS = {
    # A1 教师数据素养
    'A11': 0.2156,  # 教师数据意识与思维
    'A12': 0.2066,  # 教师数据知识与技能
    'A13': 0.1505,  # 教师数据评价与交流
    'A14': 0.2551,  # 教师数据应用与创新
    'A15': 0.1722,  # 教师数据伦理与隐私

    # A2 管理者数据素养
    'A21': 0.2462,  # 管理者数据意识与思维
    'A22': 0.1769,  # 管理者数据知识与技能
    'A23': 0.1716,  # 管理者数据评价与交流
    'A24': 0.2297,  # 管理者数据应用与创新
    'A25': 0.1756,  # 管理者数据伦理与隐私

    # A3 学生数据素养
    'A31': 0.1937,  # 学生数据意识与思维
    'A32': 0.2178,  # 学生数据知识与技能
    'A33': 0.1933,  # 学生数据评价与交流
    'A34': 0.2306,  # 学生数据应用与创新
    'A35': 0.1646,  # 学生数据伦理与隐私

    # B1 数据组织机构
    'B11': 0.4757,  # 数据领导/工作小组
    'B12': 0.5243,  # 数据组织运行情况

    # B2 数据人员配备
    'B21': 0.5833,  # 数据专职/兼职管理人员
    'B22': 0.4167,  # 数据人员进修与培训情况

    # B3 数据管理文件
    'B31': 0.5347,  # 数据管理制度类文件
    'B32': 0.4653,  # 数据实践指导类文件

    # C1 数据行为监测
    'C11': 0.3656,  # 教师数据行为
    'C12': 0.3691,  # 学生数据行为
    'C13': 0.2653,  # 管理者数据行为

    # C2 数据应用成效
    'C21': 0.4058,  # 数据应用特色成果
    'C22': 0.3641,  # 数据应用社会影响
    'C23': 0.2300,  # 应用效果主观评价

    # D1 数据资产意识
    'D11': 0.2913,  # 数据资产价值意识
    'D12': 0.4479,  # 数据资产应用意识
    'D13': 0.2608,  # 数据资产治理意识

    # D2 数据资产积累
    'D21': 1.0,  # 数据资产总量

    # E1 数据基础设施
    'E11': 0.4792,  # 数据硬件设施
    'E12': 0.5208,  # 数据系统平台

    # E2 数据安保水平
    'E21': 0.6597,  # 数据安全合规与认证
    'E22': 0.3403   # 数据风险事件记录
}

# 总分满分（5分制）
TOTAL_MAX_SCORE = 5.0


# ==================== 等级划分（5分制） ====================

# 成熟度等级划分（基于5分制总分）
MATURITY_LEVELS = [
    {'min': 4.5, 'max': 5.0, 'level': 'leading', 'name': '引领级'},
    {'min': 4.0, 'max': 4.5, 'level': 'mature', 'name': '成熟级'},
    {'min': 3.5, 'max': 4.0, 'level': 'growing', 'name': '成长级'},
    {'min': 0, 'max': 3.5, 'level': 'initial', 'name': '初始级'}
]

# 等级对应百分制（用于报告展示）
MATURITY_LEVEL_PERCENT = {
    'leading': {'min': 90, 'max': 100, 'name': '引领级'},
    'mature': {'min': 80, 'max': 90, 'name': '成熟级'},
    'growing': {'min': 70, 'max': 80, 'name': '成长级'},
    'initial': {'min': 0, 'max': 70, 'name': '初始级'}
}


# ==================== DeepSeek API 配置 ====================

DEEPSEEK_CONFIG = {
    'api_base': 'https://api.deepseek.com/v1',
    'model': 'deepseek-chat',
    'temperature': 0.7,
    'max_tokens': 500
}
