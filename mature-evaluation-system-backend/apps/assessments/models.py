"""
评估相关模型
"""
from django.db import models
from django.conf import settings


class Assessment(models.Model):
    """评估记录模型"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('collecting', '数据收集中'),
        ('analyzing', '分析中'),
        ('completed', '已完成'),
    ]
    
    MATURITY_LEVEL_CHOICES = [
        ('leading', '引领级'),
        ('mature', '成熟级'),
        ('growing', '成长级'),
        ('initial', '初始级'),
    ]
    
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='assessments',
        verbose_name='学校'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # 各维度得分
    literacy_score = models.DecimalField('数据素养得分', max_digits=8, decimal_places=4, null=True, blank=True)
    institution_score = models.DecimalField('数据制度得分', max_digits=8, decimal_places=4, null=True, blank=True)
    behavior_score = models.DecimalField('数据行为得分', max_digits=8, decimal_places=4, null=True, blank=True)
    asset_score = models.DecimalField('数据资产得分', max_digits=8, decimal_places=4, null=True, blank=True)
    technology_score = models.DecimalField('数据技术得分', max_digits=8, decimal_places=4, null=True, blank=True)
    total_score = models.DecimalField('总分', max_digits=8, decimal_places=4, null=True, blank=True)
    
    maturity_level = models.CharField('成熟度等级', max_length=20, choices=MATURITY_LEVEL_CHOICES, blank=True)
    report_file = models.FileField('报告文件', upload_to='reports/', blank=True)
    ai_suggestions = models.JSONField('AI评估建议', default=dict, blank=True)
    
    started_at = models.DateTimeField('开始时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'assessment'
        verbose_name = '评估记录'
        verbose_name_plural = '评估记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['completed_at']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.get_status_display()}"


class InstitutionAssessment(models.Model):
    """数据制度评估模型"""
    
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        related_name='institution',
        verbose_name='评估记录'
    )
    
    # 1. 数据组织机构
    has_leadership_group = models.BooleanField('是否成立领导小组', null=True, blank=True)
    meeting_activity_count = models.IntegerField('会议活动开展次数', null=True, blank=True)
    
    # 2. 数据人员配备
    has_data_staff = models.BooleanField('是否配备数据管理人员', null=True, blank=True)
    fulltime_staff_count = models.IntegerField('专职人员数量', null=True, blank=True)
    parttime_staff_count = models.IntegerField('兼职人员数量', null=True, blank=True)
    has_clear_responsibilities = models.BooleanField('是否有明确职务职责', null=True, blank=True)
    
    # 数据培训
    has_training = models.BooleanField('是否参与培训', null=True, blank=True)
    training_count = models.IntegerField('培训次数', null=True, blank=True)
    national_cert_count = models.IntegerField('国家级证书数量', null=True, blank=True)
    provincial_cert_count = models.IntegerField('省级证书数量', null=True, blank=True)
    city_cert_count = models.IntegerField('市级及以下证书数量', null=True, blank=True)
    
    # 3. 数据管理文件
    has_management_doc = models.BooleanField('是否出台管理文件', null=True, blank=True)
    management_doc_count = models.IntegerField('管理制度文件数量', null=True, blank=True)
    management_doc_files = models.JSONField('管理文件列表', default=list, blank=True)
    management_doc_analysis = models.TextField('管理文件大模型分析', blank=True, default='')
    
    # 数据实践指导文件
    has_practice_doc = models.BooleanField('是否出台实践指导文件', null=True, blank=True)
    practice_doc_count = models.IntegerField('实践指导文件数量', null=True, blank=True)
    practice_doc_files = models.JSONField('实践指导文件列表', default=list, blank=True)
    practice_doc_analysis = models.TextField('实践指导文件大模型分析', blank=True, default='')
    
    # 其他
    auto_crawled_data = models.JSONField('自动爬取的数据', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'institution_assessment'
        verbose_name = '数据制度评估'
        verbose_name_plural = '数据制度评估'
    
    def __str__(self):
        return f"{self.assessment.school.name} - 数据制度"


class BehaviorAssessment(models.Model):
    """数据行为评估模型"""
    
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        related_name='behavior',
        verbose_name='评估记录'
    )
    
    # 1. 数据行为监测
    teacher_login_freq = models.IntegerField('教师人均登录平台频次', null=True, blank=True)
    student_login_freq = models.IntegerField('学生人均登录平台频次', null=True, blank=True)
    manager_login_freq = models.IntegerField('管理者人均登录平台频次', null=True, blank=True)
    visit_count = models.IntegerField('其他学校参观学习次数', null=True, blank=True)
    
    # 2. 数据应用成效
    # 公开发表成果
    published_paper_count = models.IntegerField('已发表论文数', null=True, blank=True)
    published_book_count = models.IntegerField('已出版著作数', null=True, blank=True)
    
    # 入选优秀案例
    case_national_count = models.IntegerField('入选国家级案例数', null=True, blank=True)
    case_provincial_count = models.IntegerField('入选省级案例数', null=True, blank=True)
    case_city_count = models.IntegerField('入选市级及以下案例数', null=True, blank=True)
    
    # 荣誉奖励
    award_national_count = models.IntegerField('国家级荣誉奖励数', null=True, blank=True)
    award_provincial_count = models.IntegerField('省级荣誉奖励数', null=True, blank=True)
    award_city_count = models.IntegerField('市级及以下荣誉奖励数', null=True, blank=True)
    
    # 媒体宣传报道
    media_national_count = models.IntegerField('国家级媒体报道数', null=True, blank=True)
    media_provincial_count = models.IntegerField('省级媒体报道数', null=True, blank=True)
    media_city_count = models.IntegerField('市级及以下媒体报道数', null=True, blank=True)
    
    # 会议交流分享
    conference_national_count = models.IntegerField('国家级会议交流数', null=True, blank=True)
    conference_provincial_count = models.IntegerField('省级会议交流数', null=True, blank=True)
    conference_city_count = models.IntegerField('市级及以下会议交流数', null=True, blank=True)
    
    # 其他
    auto_crawled_data = models.JSONField('自动爬取的数据', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'behavior_assessment'
        verbose_name = '数据行为评估'
        verbose_name_plural = '数据行为评估'
    
    def __str__(self):
        return f"{self.assessment.school.name} - 数据行为"


class AssetAssessment(models.Model):
    """数据资产评估模型"""
    
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        related_name='asset',
        verbose_name='评估记录'
    )
    
    # 数据资产积累
    management_data_volume = models.DecimalField('数字管理数据总量(GB)', max_digits=10, decimal_places=2, null=True, blank=True)
    resource_data_volume = models.DecimalField('数字资源数据总量(GB)', max_digits=10, decimal_places=2, null=True, blank=True)
    service_data_volume = models.DecimalField('校园服务数据总量(GB)', max_digits=10, decimal_places=2, null=True, blank=True)
    other_data_volume = models.DecimalField('其他元数据总量(GB)', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 其他
    auto_crawled_data = models.JSONField('自动爬取的数据', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'asset_assessment'
        verbose_name = '数据资产评估'
        verbose_name_plural = '数据资产评估'
    
    def __str__(self):
        return f"{self.assessment.school.name} - 数据资产"


class TechnologyAssessment(models.Model):
    """数据技术评估模型"""
    
    DATA_CENTER_STANDARD_CHOICES = [
        ('fully_compliant', '完全符合'),
        ('partially_compliant', '部分符合'),
        ('not_compliant', '不符合'),
    ]

    CLOUD_DEDICATED_FULFILL_CHOICES = [
        ('fully_meets', '完全达到'),
        ('partially_meets', '部分达到'),
        ('not_meets', '未达到'),
    ]
    
    DEVICE_RATIO_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]
    
    SECURITY_RATIO_CHOICES = [
        ('low', '低于40%'),
        ('medium', '40%-80%'),
        ('high', '高于80%'),
    ]
    
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        related_name='technology',
        verbose_name='评估记录'
    )
    
    # 1. 数据基础设施
    data_center_standard = models.CharField('数据中心标准符合度', max_length=30, choices=DATA_CENTER_STANDARD_CHOICES, blank=True, null=True)
    cloud_dedicated_service = models.CharField('专享云服务完全满足需求情况', max_length=30, choices=CLOUD_DEDICATED_FULFILL_CHOICES, blank=True, null=True)
    student_device_ratio = models.CharField('生机比', max_length=20, choices=DEVICE_RATIO_CHOICES, blank=True, null=True)
    teacher_device_ratio = models.CharField('师机比', max_length=20, choices=DEVICE_RATIO_CHOICES, blank=True, null=True)
    has_data_platform = models.BooleanField('是否建设数据治理平台', null=True, blank=True)
    
    # 2. 数据安全水平
    security_certified_count = models.IntegerField('通过安保等级认定数量', null=True, blank=True)
    security_certified_ratio = models.CharField('通过安保等级认定比例', max_length=20, choices=SECURITY_RATIO_CHOICES, blank=True, null=True)
    has_security_incident = models.BooleanField('是否发生数据风险事件', null=True, blank=True)
    
    # 其他
    auto_crawled_data = models.JSONField('自动爬取的数据', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'technology_assessment'
        verbose_name = '数据技术评估'
        verbose_name_plural = '数据技术评估'
    
    def __str__(self):
        return f"{self.assessment.school.name} - 数据技术"
