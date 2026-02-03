"""
报告生成异步任务
"""
import logging
from celery import shared_task
from django.utils import timezone
from apps.assessments.models import Assessment
from .report_service import ReportService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_assessment_report(self, assessment_id: int):
    """
    生成评估报告的异步任务
    :param assessment_id: 评估ID
    :return: 任务结果
    """
    logger.info(f"开始生成评估报告任务，评估ID: {assessment_id}")
    
    try:
        # 获取评估记录
        assessment = Assessment.objects.get(id=assessment_id)

        # 注意：不检查status状态，报告生成时会自动计算得分并更新状态
        logger.info(f"评估 {assessment_id} 当前状态: {assessment.status}")

        # 创建报告服务
        report_service = ReportService(assessment)
        
        # 生成报告
        result = report_service.generate_report()
        
        # 如果成功，发送邮件
        if result['success']:
            logger.info(f"报告生成成功，准备发送邮件")
            report_service.send_report_email()
        
        return result
        
    except Assessment.DoesNotExist:
        logger.error(f"评估 {assessment_id} 不存在")
        return {
            'success': False,
            'message': '评估不存在'
        }
    
    except Exception as e:
        logger.error(f"生成报告任务失败: {str(e)}", exc_info=True)
        
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"任务失败，准备重试 (第{self.request.retries + 1}次)")
            raise self.retry(exc=e, countdown=60)  # 60秒后重试
        
        return {
            'success': False,
            'message': f'报告生成失败: {str(e)}'
        }

