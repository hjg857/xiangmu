"""
测试计分系统
"""
from django.core.management.base import BaseCommand
from apps.assessments.models import Assessment
from apps.assessments.scoring_service import ScoringService
from apps.assessments.llm_service import LLMService


class Command(BaseCommand):
    help = '测试计分系统'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--assessment-id',
            type=int,
            help='评估记录ID'
        )
        parser.add_argument(
            '--test-llm',
            action='store_true',
            help='测试大模型API连接'
        )
    
    def handle(self, *args, **options):
        # 测试大模型连接
        if options['test_llm']:
            self.stdout.write('测试DeepSeek API连接...')
            llm_service = LLMService()
            result = llm_service.test_connection()
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f'✓ {result["message"]}'))
                self.stdout.write(f'响应: {result["response"]}')
            else:
                self.stdout.write(self.style.ERROR(f'✗ {result["message"]}'))
            return
        
        # 测试计分
        assessment_id = options.get('assessment_id')
        if not assessment_id:
            self.stdout.write(self.style.ERROR('请指定评估记录ID: --assessment-id=<id>'))
            return
        
        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'评估记录 {assessment_id} 不存在'))
            return
        
        self.stdout.write(f'开始计算评估 {assessment_id} 的得分...')
        self.stdout.write(f'学校: {assessment.school.name}')
        self.stdout.write(f'状态: {assessment.get_status_display()}')
        self.stdout.write('-' * 50)
        
        # 创建计分服务
        scoring_service = ScoringService(assessment)
        
        # 计算各维度得分
        self.stdout.write('\n计算数据素养得分...')
        literacy_score = scoring_service.calculate_literacy_score()
        self.stdout.write(self.style.SUCCESS(f'数据素养得分: {literacy_score}'))
        
        self.stdout.write('\n计算数据制度得分...')
        institution_score = scoring_service.calculate_institution_score()
        self.stdout.write(self.style.SUCCESS(f'数据制度得分: {institution_score}'))
        
        self.stdout.write('\n计算数据行为得分...')
        behavior_score = scoring_service.calculate_behavior_score()
        self.stdout.write(self.style.SUCCESS(f'数据行为得分: {behavior_score}'))
        
        self.stdout.write('\n计算数据资产得分...')
        asset_score = scoring_service.calculate_asset_score()
        self.stdout.write(self.style.SUCCESS(f'数据资产得分: {asset_score}'))
        
        self.stdout.write('\n计算数据技术得分...')
        technology_score = scoring_service.calculate_technology_score()
        self.stdout.write(self.style.SUCCESS(f'数据技术得分: {technology_score}'))
        
        # 计算总分
        total_score = (literacy_score + institution_score + behavior_score + 
                      asset_score + technology_score)
        maturity_level = scoring_service.determine_maturity_level(total_score)
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'总分: {total_score}'))
        self.stdout.write(self.style.SUCCESS(f'成熟度等级: {maturity_level}'))
        self.stdout.write('=' * 50)
