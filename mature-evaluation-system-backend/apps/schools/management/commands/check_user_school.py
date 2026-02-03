"""
检查用户和学校关联的管理命令
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.schools.models import School


class Command(BaseCommand):
    help = '检查用户和学校的关联关系'

    def handle(self, *args, **options):
        self.stdout.write('开始检查用户和学校关联...')
        
        # 获取所有学校用户
        school_users = User.objects.filter(role='school')
        self.stdout.write(f'找到 {school_users.count()} 个学校用户')
        
        for user in school_users:
            self.stdout.write(f'\n用户: {user.username} (ID: {user.id})')
            self.stdout.write(f'  邮箱: {user.email}')
            
            # 检查是否有关联的School
            try:
                school = user.school
                self.stdout.write(self.style.SUCCESS(f'  ✓ 已关联学校: {school.name} (ID: {school.id})'))
            except School.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'  ✗ 未关联学校'))
                
                # 尝试查找可能的School记录
                schools = School.objects.filter(user=user)
                if schools.exists():
                    self.stdout.write(f'    但找到 {schools.count()} 条School记录:')
                    for s in schools:
                        self.stdout.write(f'      - {s.name} (ID: {s.id})')
                else:
                    self.stdout.write('    也没有找到任何School记录')
        
        self.stdout.write(self.style.SUCCESS('\n检查完成！'))
