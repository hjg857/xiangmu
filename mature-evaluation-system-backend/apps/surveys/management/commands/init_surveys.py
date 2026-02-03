"""
初始化问卷数据的管理命令
"""
from django.core.management.base import BaseCommand
from apps.surveys.models import SurveyTemplate, SurveyQuestion


class Command(BaseCommand):
    help = '初始化三份问卷数据（教师、学生、管理者）'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化问卷数据...')
        
        # 清空现有数据
        SurveyQuestion.objects.all().delete()
        SurveyTemplate.objects.all().delete()
        
        # 创建教师问卷
        self.create_teacher_survey()
        
        # 创建学生问卷
        self.create_student_survey()
        
        # 创建管理者问卷
        self.create_manager_survey()
        
        self.stdout.write(self.style.SUCCESS('问卷数据初始化完成！'))

    def create_teacher_survey(self):
        """创建教师问卷"""
        self.stdout.write('创建教师问卷...')
        
        template = SurveyTemplate.objects.create(
            survey_type='teacher',
            title='中小学校教师数据素养及数据应用效果调查问卷',
            description='''尊敬的老师：
您好！为深入了解您所在学校教师数据素养的整体发展现状，以及各位教师对学校数据应用成效的主观评价，特设计《中小学校教师数据素养及数据应用效果调查问卷》，诚邀您根据实际情况进行填写。
此次调查严格遵循专业伦理与规范要求，确保您的个人隐私得到充分保护。您的回答无对错之分，请放心填写。
衷心感谢您的支持与参与！''',
            is_active=True
        )
        
        # 第一部分：个人基本信息
        questions_part1 = [
            {
                'question_text': '您的性别：',
                'question_type': 'single_choice',
                'options': ['男', '女'],
                'order': 1,
                'is_required': True
            },
            {
                'question_text': '您的年龄：',
                'question_type': 'single_choice',
                'options': ['30岁及以下', '31-40岁', '41-50岁', '51岁及以上'],
                'order': 2,
                'is_required': True
            },
            {
                'question_text': '所教学段：',
                'question_type': 'single_choice',
                'options': ['小学', '初中', '高中'],
                'order': 3,
                'is_required': True
            },
            {
                'question_text': '学校所在地区：',
                'question_type': 'single_choice',
                'options': ['城市', '城乡结合部', '乡村'],
                'order': 4,
                'is_required': True
            },
            {
                'question_text': '所教学科：',
                'question_type': 'single_choice',
                'options': ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理', '体育', '音乐', '美术', '信息技术', '其他'],
                'order': 5,
                'is_required': True
            }
        ]
        
        for q_data in questions_part1:
            SurveyQuestion.objects.create(template=template, **q_data)
        
        # 第二部分：数据素养自我评价量表
        # 一、数据意识与思维（A11，8题，40分）
        dimension1_questions = [
            '我对教育数据具有一定洞察力和判断力。',
            '我具有主动使用教育数据解决教学问题的意识。',
            '我能够以严谨认真的态度对待和使用教育数据。',
            '我认识到数据在教育教学中具有重要作用和价值。',
            '我能够将学生以及自身行为以数据化的方式进行呈现。',
            '我能够建立数据与教学现象间的联系，使用数据对教学现象进行解释和优化。',
            '我能够从多角度分析数据，充分挖掘数据的在教育教学过程的隐藏价值。',
            '我能够对数据分析结果进行批判、质疑，并提出改进意见。'
        ]
        
        scale_options = ['非常不符合', '不符合', '一般', '符合', '非常符合']
        score_rule = {'非常不符合': 1, '不符合': 2, '一般': 3, '符合': 4, '非常符合': 5}
        
        order = 6
        for q_text in dimension1_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1

        # 二、数据知识与技能（A12，7题，35分）
        dimension2_questions = [
            '我了解教育数据的内涵及其在教育教学中的主要应用方式。',
            '我知道不同类型数据的分析方法及其适用情境。',
            '我能够从合理渠道获取目标数据。',
            '我能够根据需要对数据进行筛选加工。',
            '我能够掌握基本数据处理工具（如Excel、WPS、SPSS等）的操作方法。',
            '我能够使用可视化软件对数据进行可视化处理和呈现。',
            '我能够对数据处理结果作出合理解释和推断。'
        ]
        
        for q_text in dimension2_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 三、数据评价与交流（A13，3题，15分）
        dimension3_questions = [
            '我能够对数据使用环节进行回顾反思，评价数据使用效果。',
            '我能够通过教师间的数据交流相互促进。',
            '我能够在合理合法范围内与相关利益者共享数据成果。'
        ]
        
        for q_text in dimension3_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 四、数据应用与创新（A14，8题，40分）
        dimension4_questions = [
            '我能够利用多种类型数据对学生进行多元评价。',
            '我具备使用数据评估教学过程和效果的能力。',
            '我能够通过数据发现教学问题，或通过数据寻求问题的解决方式。',
            '我能够根据数据处理结果调整教学行为。',
            '我能够使用数据优化课堂教学、改善教学效果。',
            '我用数据让知识变得更有说服力、优化教学内容以及提升知识点的科学性。',
            '我能够基于数据分析结果创新教学方法与策略。',
            '我能够利用数据优化教育理念与评价方式。'
        ]
        
        for q_text in dimension4_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 五、数据伦理与隐私（A15，3题，15分）
        dimension5_questions = [
            '我能够有意识地对隐私数据进行保护。',
            '我能够在法律和道德允许的范围内获取和使用数据。',
            '我能够尊重他人的数据，使用时能够注明出处。'
        ]
        
        for q_text in dimension5_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 第三部分：数据应用效果主观评价量表
        part3_questions = [
            '我认为学校当前具备较完善的数据应用支持（如平台工具、指导培训或技术帮助等），能够支撑日常教学和学习活动。',
            '我认为学校在教学中应用数据的方式具有针对性，能够有效回应教学中的具体问题。',
            '我认为学校提供的数据报告或分析结果具备较强的专业性，能为教学提供明确的解释与参考。',
            '我认为学校基于数据所采取的教学或管理措施成效明显，有助于提升教学效率与学生学习成效。',
            '我认为学校建立了相对完善的数据应用流程（如数据分析、呈现反馈等），能持续支持教学应用。',
            '我对学校整体的数据应用情况感到满意。'
        ]
        
        for q_text in part3_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        self.stdout.write(self.style.SUCCESS(f'  教师问卷创建完成，共 {order-1} 题'))

    def create_student_survey(self):
        """创建学生问卷"""
        self.stdout.write('创建学生问卷...')
        
        template = SurveyTemplate.objects.create(
            survey_type='student',
            title='中小学校学生数据素养及数据应用效果调查问卷',
            description='''尊敬的同学：
您好！为深入了解您所在学校学生数据素养的整体发展现状，以及各位同学对学校数据应用成效的主观评价，特设计《中小学校学生数据素养及数据应用效果调查问卷》，诚邀您根据实际情况进行填写。
此次调查严格遵循专业伦理与规范要求，确保您的个人隐私得到充分保护。您的回答无对错之分，请放心填写。
衷心感谢您的支持与参与！''',
            is_active=True
        )
        
        # 第一部分：个人基本信息
        questions_part1 = [
            {
                'question_text': '您的性别：',
                'question_type': 'single_choice',
                'options': ['男', '女'],
                'order': 1,
                'is_required': True
            },
            {
                'question_text': '所处学段：',
                'question_type': 'single_choice',
                'options': ['小学', '初中', '高中'],
                'order': 2,
                'is_required': True
            },
            {
                'question_text': '学校所在地区：',
                'question_type': 'single_choice',
                'options': ['城市', '城乡结合部', '乡村'],
                'order': 3,
                'is_required': True
            }
        ]
        
        for q_data in questions_part1:
            SurveyQuestion.objects.create(template=template, **q_data)
        
        # 第二部分：数据素养自我评价量表
        scale_options = ['非常不符合', '不符合', '一般', '符合', '非常符合']
        score_rule = {'非常不符合': 1, '不符合': 2, '一般': 3, '符合': 4, '非常符合': 5}
        
        # 一、数据意识与思维（A31，7题，35分）
        dimension1_questions = [
            '我能够注意到学习过程中产生的各类数据（如成绩、学习时间、错题等）。',
            '我具有主动使用数据来发现问题、改进学习方法和提高学习效率的意识。',
            '我能够以严谨认真的态度对待和使用教育数据。',
            '我能够尝试将学习活动（如背单词、写作业等）转化为数据来记录和分析。',
            '我能够将学习数据与学习现象（如成绩波动等）联系起来，并发现原因或优化方法。',
            '我能够从不同角度理解和分析学习数据，发现其中潜藏的信息。',
            '我遇到异常或不合理的数据时，能提出质疑并进一步思考其背后原因。'
        ]
        
        order = 4
        for q_text in dimension1_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 二、数据知识与技能（A32，7题，35分）
        dimension2_questions = [
            '我理解什么是教育数据，以及这些数据在学习和生活中的作用。',
            '我知道常见的数据类型（如成绩、作业数据等）以及它们的用途。',
            '我能够根据需要从学校提供的平台或其它可靠渠道获取学习相关数据。',
            '我能够筛选对学习有帮助的数据，并对它们进行简单整理。',
            '我能够掌握基本数据处理工具（如Excel、WPS等）的操作方法。',
            '我能够将数据以图表（如柱状图、折线图等）的方式进行处理和呈现。',
            '我能够对学校平台提供的图表或数据进行合理解释和判断。'
        ]
        
        for q_text in dimension2_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 三、数据评价与交流（A33，2题，10分）
        dimension3_questions = [
            '我能够对自己使用学习数据的过程进行反思，并判断是否有效帮助了学习。',
            '我能够和同学分享使用数据的过程或经验，从中获得学习建议或提高。'
        ]
        
        for q_text in dimension3_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 四、数据应用与创新（A34，6题，30分）
        dimension4_questions = [
            '我能够通过学习数据（如成绩、练习结果等）分析自己的学习表现。',
            '我能够根据学习平台或系统给出的数据反馈调整学习计划。',
            '当遇到学习困难时，我愿意借助数据寻找解决方法。',
            '我能够根据数据结果调整自己的学习方式（如背诵、练习方式等）。',
            '我能够利用数据工具（如图表、数据平台等）更好地整理和理解学习内容。',
            '我能够使用数据进行创新表达，比如用数据讲故事、做展示等。'
        ]
        
        for q_text in dimension4_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 五、数据伦理与隐私（A35，3题，15分）
        dimension5_questions = [
            '我能够有意识地对隐私数据进行保护。',
            '我在法律和道德允许的范围内获取和使用数据。',
            '我能够尊重他人的数据，使用时能够注明出处。'
        ]
        
        for q_text in dimension5_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 第三部分：数据应用效果评价量表
        part3_questions = [
            '我认为学校提供了充分的数据工具与指导（如数据平台、培训讲解等），以支持我的学习。',
            '我认为学校在平台上呈现的数据（如作业成绩、测验结果等）能够真实反映我的学习情况，并帮助我改进学习行为。',
            '我认为学校提供的学习分析报告或反馈内容清晰明确，能够帮助我了解自身的优势与不足。',
            '我发现教师会根据测验、作业等数据，及时调整教学方法或内容，使我的学习更加高效。',
            '我认为学校在收集和使用数据时操作规范，不影响我正常学习，也能有效保护我的隐私。',
            '我对学校整体的数据应用情况感到满意。'
        ]
        
        for q_text in part3_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        self.stdout.write(self.style.SUCCESS(f'  学生问卷创建完成，共 {order-1} 题'))


    def create_manager_survey(self):
        """创建管理者问卷"""
        self.stdout.write('创建管理者问卷...')
        
        template = SurveyTemplate.objects.create(
            survey_type='manager',
            title='中小学校管理者数据素养及数据资产意识调查问卷',
            description='''尊敬的老师：
您好！为深入了解您所在学校管理者的数据素养及数据资产意识的整体发展现状，特设计《中小学校管理者数据素养及数据资产意识调查问卷》，诚邀您根据实际情况进行填写。
此次调查严格遵循专业伦理与规范要求，确保您的个人隐私得到充分保护。您的回答无对错之分，请放心填写。
衷心感谢您的支持与参与！''',
            is_active=True
        )
        
        # 第一部分：个人基本信息
        questions_part1 = [
            {
                'question_text': '您的性别：',
                'question_type': 'single_choice',
                'options': ['男', '女'],
                'order': 1,
                'is_required': True
            },
            {
                'question_text': '您的年龄：',
                'question_type': 'single_choice',
                'options': ['30岁及以下', '31-40岁', '41-50岁', '51岁及以上'],
                'order': 2,
                'is_required': True
            },
            {
                'question_text': '您担任学校管理工作的年限：',
                'question_type': 'single_choice',
                'options': ['1年以下', '1-5年', '6-10年', '11-15年', '16-20年', '21-25年', '26-30年', '30年以上'],
                'order': 3,
                'is_required': True
            },
            {
                'question_text': '您的学校性质：',
                'question_type': 'single_choice',
                'options': ['小学', '初中', '九年一贯', '完全中学', '高中', '十二年一贯制学校'],
                'order': 4,
                'is_required': True
            },
            {
                'question_text': '学校所在地区：',
                'question_type': 'single_choice',
                'options': ['城市', '城乡结合部', '乡村'],
                'order': 5,
                'is_required': True
            },
            {
                'question_text': '您的职务是：',
                'question_type': 'single_choice',
                'options': ['校长', '副校长', '教务主任', '德育主任', '教研主任', '年级主任', '其他'],
                'order': 6,
                'is_required': True
            }
        ]
        
        for q_data in questions_part1:
            SurveyQuestion.objects.create(template=template, **q_data)
        
        # 第二部分：数据素养自我评价量表
        scale_options = ['非常不符合', '不符合', '一般', '符合', '非常符合']
        score_rule = {'非常不符合': 1, '不符合': 2, '一般': 3, '符合': 4, '非常符合': 5}
        
        # 一、数据意识与思维（A21，8题，40分）
        dimension1_questions = [
            '我具备识别教育管理工作中关键数据的敏感性。',
            '我具有主动运用具有数据解决学校教育教学或治理问题的意识。',
            '我能够以科学、规范、审慎的态度管理和使用教育数据。',
            '我能够认识到教育数据对提升学校决策质量、教学成效和治理效能等的重要价值。',
            '我能够将教育管理与教学行为过程数据化、结构化地呈现出来。',
            '我能够将数据与教育教学现象建立联系，以数据支撑问题判断与策略优化。',
            '我能够从不同视角分析教育数据，深入挖掘其背后潜在的教育价值。',
            '我能够质疑异常或偏离预期的数据结果，并探究其形成原因。'
        ]
        
        order = 7
        for q_text in dimension1_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 二、数据知识与技能（A22，8题，40分）
        dimension2_questions = [
            '我了解教育数据的基本内涵及在学校管理中的主要应用方式。',
            '我知道不同类型数据的分析方法及其适用情境。',
            '我了解国家或学校数据治理相关政策文件、标准规范或制度框架的基本内容。',
            '我能够确定教育决策所需的数据类型，并从合规渠道组织采集相关数据。',
            '我具备对原始数据进行筛选、清洗、整理的基本能力。',
            '我能够熟练操作基本数据处理工具（如Excel、WPS、SPSS等），用于学校管理。',
            '我能够使用可视化工具（如图表、仪表板等）对教育数据进行可视化处理和呈现。',
            '我能够对数据分析结果进行合理解释，并识别其中的关键问题或发展趋势。'
        ]
        
        for q_text in dimension2_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 三、数据评价与交流（A23，3题，15分）
        dimension3_questions = [
            '我能够对学校或自身数据使用的各个环节进行回顾、反思，并对数据使用的效果进行系统评价。',
            '我能够推动在校内建立常态化的数据沟通与反馈机制（如定期简报、例会等）。',
            '我能够在合理、合法的范围内，与教师、学生、家长或主管部门共享相关数据成果。'
        ]
        
        for q_text in dimension3_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 四、数据应用与创新（A24，8题，40分）
        dimension4_questions = [
            '我能够利用多种类型数据对学校师生发展、部门运行情况等进行多元化评价。',
            '我具备使用数据科学评估学校管理过程与政策实施效果的能力。',
            '我能够通过数据发现教育管理的问题，并据此分析原因、提出改进方案。',
            '我能够根据数据分析结果及时调整管理策略和日常决策行为。',
            '我能够运用数据推动部门之间的协作机制优化，提高整体管理效能。',
            '我能够借助数据增强决策的科学性与说服力，提升学校管理水平。',
            '我能够基于数据分析结果提出创新管理策略，推动学校制度或流程的改革与发展。',
            '我能够利用数据优化管理理念和操作流程，提升教育治理质量和效率。'
        ]
        
        for q_text in dimension4_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 五、数据伦理与隐私（A25，4题，20分）
        dimension5_questions = [
            '我能够在数据处理过程中自觉保护学生、教师和自身等的隐私信息。',
            '我能够在法律法规和职业道德允许的范围内获取、处理和使用教育数据。',
            '我能够尊重他人数据的知识产权，在使用或引用他人数据成果时注明来源。',
            '我能够识别学校在教育数据使用过程中可能存在的伦理或隐私风险，并制定相应的防范与应对措施。'
        ]
        
        for q_text in dimension5_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 第三部分：数据资产意识评价量表
        # 一、数据资产价值意识
        part3_section1 = [
            '我认为学校积累的各类数据是一种重要的战略资源。',
            '我认为数据资产能够为学校的教育教学、管理和决策等过程提供有力支持。',
            '我认为学校应加强数据资产的评估与价值挖掘，以提升数据利用效率和效能。',
            '我认为学校应将数据资产纳入长期发展规划，以提升教育质量和管理水平。'
        ]
        
        for q_text in part3_section1:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 二、数据资产应用意识
        part3_section2 = [
            '我会主动探索数据资产在提升学校教学质量和管理效果的应用。',
            '我会引导教师和学生重视数据资产的应用，以提升全校数据应用意识与能力。',
            '我会合理规划数据资产的使用，确保数据服务于学校的长期发展目标。',
            '我会利用数据资产来支持学校的创新实践和改革探索。'
        ]
        
        for q_text in part3_section2:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 三、数据资产治理意识
        part3_section3 = [
            '我认为数据清洗和整理有助于提高数据的准确性、完整性和一致性。',
            '我认为应定期检查和维护学校数据，以保障数据质量，支撑教育应用实践。',
            '我认为对数据进行识别与分类有助于提升数据的可用性和可解释性。',
            '我认为数据应用过程中应注重权限设置与管理，以确保用途可控、可追溯。',
            '我认为识别和防范数据应用风险，有助于提升数据使用的安全性和可控性。',
            '我认为学校应形成数据制度文件，以规范数据的采集、存储和使用等全过程。'
        ]
        
        for q_text in part3_section3:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        # 第四部分：数据应用效果评价量表
        part4_questions = [
            '我认为学校当前具备较完善的数据应用支持（如平台工具、指导培训或技术帮助等），能够支撑日常教学和管理活动。',
            '我认为学校整体的数据应用覆盖了教学、学习、评价、管理等多个场景，具有明显成效。',
            '我认为学校已基本建立完善的数据应用过程（如数据采集、分析、呈现、反馈等），能够持续支持教学与管理优化。',
            '我认为学校目前的数据应用氛围良好，教师、学生和管理人员均认可数据在教育中的价值与作用。',
            '我对学校当前的数据应用效果总体满意。'
        ]
        
        for q_text in part4_questions:
            SurveyQuestion.objects.create(
                template=template,
                question_text=q_text,
                question_type='scale',
                options=scale_options,
                score_rule=score_rule,
                order=order,
                is_required=True
            )
            order += 1
        
        self.stdout.write(self.style.SUCCESS(f'  管理者问卷创建完成，共 {order-1} 题'))
