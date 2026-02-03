"""
初始化内容页面数据
"""
from django.core.management.base import BaseCommand
from apps.admin_panel.models import ContentPage


class Command(BaseCommand):
    help = '初始化内容页面数据'

    def handle(self, *args, **options):
        content_pages = [
            {
                'page_key': 'about',
                'title': '关于我们',
                'content': '''
                <h2>项目背景</h2>
                <p>在教育数字化转型的大背景下，数据已成为推动教育改革与发展的重要驱动力。中小学校数据文化成熟度评估监测系统应运而生，旨在帮助学校全面了解自身数据文化建设现状，科学评估数据应用能力。</p>
                
                <h2>项目愿景</h2>
                <p>我们致力于推动中小学校建立数据驱动的教育决策机制，培育良好的数据文化氛围，提升教育质量和管理效能。</p>
                
                <h2>核心价值</h2>
                <ul>
                    <li>科学评估：基于五维度评估模型，全面诊断学校数据文化成熟度</li>
                    <li>精准诊断：通过量化指标和智能分析，精准定位问题与差距</li>
                    <li>持续改进：提供可视化报告和改进建议，助力学校持续提升</li>
                </ul>
                
                <h2>联系我们</h2>
                <p>地址：江苏省徐州市铜山新区上海路101号</p>
                <p>邮箱：a18398917485@163.com</p>
                ''',
                'order': 1,
                'is_published': True
            },
            {
                'page_key': 'culture',
                'title': '数据文化',
                'content': '''
                <h2>什么是数据文化</h2>
                <p>数据文化是指组织内部形成的以数据为核心的价值观、行为规范和工作方式。在教育领域，数据文化强调用数据说话、用数据决策、用数据创新。</p>
                
                <h2>为什么重要</h2>
                <p>良好的数据文化能够：</p>
                <ul>
                    <li>提升教育决策的科学性和精准性</li>
                    <li>促进教学质量的持续改进</li>
                    <li>优化学校管理效能</li>
                    <li>推动教育公平与个性化发展</li>
                </ul>
                
                <h2>建设路径</h2>
                <p>数据文化建设需要从数据素养、数据制度、数据行为、数据资产、数据技术五个维度协同推进。</p>
                ''',
                'order': 2,
                'is_published': True
            },
            {
                'page_key': 'guide',
                'title': '评估说明',
                'content': '''
                <h2>评估维度</h2>
                <p>本系统从五个维度对学校数据文化成熟度进行评估：</p>
                
                <h3>1. 数据素养（20分）</h3>
                <p>评估教师、学生、管理者的数据意识、数据能力和数据应用水平。</p>
                
                <h3>2. 数据制度（20分）</h3>
                <p>评估学校数据管理制度建设、组织保障和安全规范等方面。</p>
                
                <h3>3. 数据行为（20分）</h3>
                <p>评估学校在教学、管理等场景中的数据应用实践和创新案例。</p>
                
                <h3>4. 数据资产（20分）</h3>
                <p>评估学校数据资源的积累、管理和共享开放情况。</p>
                
                <h3>5. 数据技术（20分）</h3>
                <p>评估学校数据基础设施、技术工具和平台建设水平。</p>
                
                <h2>评估流程</h2>
                <ol>
                    <li>注册登录：学校申请账号并通过审批</li>
                    <li>数据采集：填写评估问卷和相关信息</li>
                    <li>智能分析：系统自动计算各维度得分</li>
                    <li>报告生成：生成可视化评估报告</li>
                    <li>持续改进：根据报告建议制定改进计划</li>
                </ol>
                
                <h2>成熟度等级</h2>
                <ul>
                    <li>卓越（90-100分）：数据文化建设处于领先水平</li>
                    <li>优秀（80-89分）：数据文化建设成效显著</li>
                    <li>良好（70-79分）：数据文化建设稳步推进</li>
                    <li>合格（60-69分）：数据文化建设初见成效</li>
                    <li>待改进（0-59分）：数据文化建设有待加强</li>
                </ul>
                ''',
                'order': 3,
                'is_published': True
            },
            {
                'page_key': 'news',
                'title': '实践动态',
                'content': '''
                <h2>最新动态</h2>
                <p>敬请期待...</p>
                
                <h2>优秀案例</h2>
                <p>我们将持续分享各地中小学校在数据文化建设方面的优秀实践案例。</p>
                ''',
                'order': 4,
                'is_published': True
            }
        ]
        
        for page_data in content_pages:
            page, created = ContentPage.objects.update_or_create(
                page_key=page_data['page_key'],
                defaults={
                    'title': page_data['title'],
                    'content': page_data['content'],
                    'order': page_data['order'],
                    'is_published': page_data['is_published']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'成功创建内容页面: {page.title}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'成功更新内容页面: {page.title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('内容页面初始化完成！')
        )
