"""
为现有用户创建School记录的管理命令
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.schools.models import School


class Command(BaseCommand):
    help = '为现有的学校用户创建School记录'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='用户名')
        parser.add_argument('--school-name', type=str, required=True, help='学校名称')
        parser.add_argument('--school-type', type=str, default='primary', 
                          choices=['primary', 'junior', 'senior', 'nine_year', 'twelve_year'],
                          help='学校类型')
        parser.add_argument('--province', type=str, default='北京市', help='省份')
        parser.add_argument('--city', type=str, default='北京市', help='城市')
        parser.add_argument('--district', type=str, default='', help='区县')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'用户 {username} 不存在'))
            return
        
        # 检查是否已有School记录
        if hasattr(user, 'school'):
            self.stdout.write(self.style.WARNING(f'用户 {username} 已有School记录'))
            return
        
        # 创建School记录
        school = School.objects.create(
            user=user,
            name=options['school_name'],
            school_type=options['school_type'],
            province=options['province'],
            city=options['city'],
            district=options['district'],
            contact_name=user.username,
            contact_position='管理员',
            contact_phone='',
            contact_email=user.email
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'成功为用户 {username} 创建School记录：{school.name}'
        ))
