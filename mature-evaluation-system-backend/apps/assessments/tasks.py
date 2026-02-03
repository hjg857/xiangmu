"""
评估相关的Celery异步任务
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def calculate_assessment_scores(self, assessment_id):
    """
    计算评估得分的异步任务
    
    :param assessment_id: 评估记录ID
    """
    from .models import Assessment
    from .scoring_service import ScoringService
    from .llm_service import LLMService
    
    try:
        logger.info(f"开始计算评估 {assessment_id} 的得分")
        
        # 获取评估记录
        assessment = Assessment.objects.get(id=assessment_id)
        
        # 更新状态为分析中
        assessment.status = 'analyzing'
        assessment.save()
        
        # 调用大模型评分文件质量（如果有文件）
        try:
            institution = assessment.institution
            llm_service = LLMService()
            
            # 评分管理制度文件
            if institution.has_management_doc and institution.management_doc_files:
                logger.info("开始评分管理制度文件")
                # TODO: 读取文件内容并评分
                # 这里需要实现文件读取逻辑
                pass
            
            # 评分实践指导文件
            if institution.has_practice_doc and institution.practice_doc_files:
                logger.info("开始评分实践指导文件")
                # TODO: 读取文件内容并评分
                pass
        except Exception as e:
            logger.warning(f"大模型评分过程出错: {str(e)}")
            # 继续执行，不影响其他计分
        
        # 创建计分服务并计算得分
        scoring_service = ScoringService(assessment)
        scores = scoring_service.calculate_all_scores()
        
        # 更新评估记录
        assessment.literacy_score = scores['literacy_score']
        assessment.institution_score = scores['institution_score']
        assessment.behavior_score = scores['behavior_score']
        assessment.asset_score = scores['asset_score']
        assessment.technology_score = scores['technology_score']
        assessment.total_score = scores['total_score']
        assessment.maturity_level = scores['maturity_level']
        assessment.status = 'completed'
        assessment.completed_at = timezone.now()
        
        # 生成AI建议（异步预生成）
        try:
            logger.info("开始生成AI评估建议")
            from apps.reports.report_data_service import ReportDataService
            from apps.reports.report_ai_service import ReportAIService
            
            # 准备数据
            data_service = ReportDataService(assessment, scoring_service=scoring_service)
            report_data = data_service.get_all_report_data()
            
            # 生成建议
            ai_service = ReportAIService()
            suggestions = ai_service.generate_all_suggestions(report_data)
            assessment.ai_suggestions = suggestions
            logger.info("AI评估建议生成完成")
        except Exception as e:
            logger.error(f"生成AI建议失败: {str(e)}", exc_info=True)
            # 建议生成失败不影响整体流程，只是下次查看时需要重新生成
        
        assessment.save()

        # 发送邮件通知
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            school_name = assessment.school.name
            email = assessment.school.contact_email
            
            subject = f'【数据文化成熟度评估系统】评估报告生成通知'
            message = f"""
尊敬的 {school_name} 用户：

您好！

您的学校数据文化成熟度评估报告已生成完毕。

您可以登录系统查看详细报告

感谢您的使用！

---
数据文化研究中心
{settings.SYSTEM_EMAIL_SIGNATURE}
"""
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER or 'noreply@example.com',
                recipient_list=[email],
                fail_silently=True,
            )
            logger.info(f"评估完成通知邮件已发送至: {email}")
        except Exception as e:
            logger.error(f"发送评估完成通知邮件失败: {str(e)}")
        
        logger.info(f"评估 {assessment_id} 计分完成，总分: {scores['total_score']}")
        
        return {
            'success': True,
            'assessment_id': assessment_id,
            'scores': {k: str(v) for k, v in scores.items()}
        }
        
    except Assessment.DoesNotExist:
        logger.error(f"评估记录 {assessment_id} 不存在")
        return {
            'success': False,
            'error': '评估记录不存在'
        }
    
    except Exception as e:
        logger.error(f"计算评估 {assessment_id} 得分失败: {str(e)}", exc_info=True)
        
        # 重试
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            assessment.status = 'draft'  # 恢复为草稿状态
            assessment.save()
        except:
            pass
        
        # 如果还有重试次数，则重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)  # 60秒后重试
        
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def score_document_with_llm(document_path, document_type):
    """
    使用大模型评分文档的异步任务
    
    :param document_path: 文档路径
    :param document_type: 文档类型 ('management' 或 'practice')
    """
    from .llm_service import LLMService
    from django.core.files.storage import default_storage
    
    try:
        logger.info(f"开始评分文档: {document_path}")
        
        # 读取文件内容
        if default_storage.exists(document_path):
            with default_storage.open(document_path, 'r') as f:
                content = f.read()
        else:
            logger.error(f"文件不存在: {document_path}")
            return {'success': False, 'error': '文件不存在'}
        
        # 调用大模型评分
        llm_service = LLMService()
        if document_type == 'management':
            result = llm_service.score_management_document(content)
        elif document_type == 'practice':
            result = llm_service.score_practice_document(content)
        else:
            return {'success': False, 'error': '无效的文档类型'}
        
        logger.info(f"文档评分完成: {document_path}, 得分: {result['score']}")
        return result
        
    except Exception as e:
        logger.error(f"文档评分失败: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }
