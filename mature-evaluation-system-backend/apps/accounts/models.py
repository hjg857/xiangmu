"""
用户认证相关模型
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """自定义用户管理器"""
    
    def create_user(self, username, email, password=None, **extra_fields):
        """创建普通用户"""
        if not username:
            raise ValueError('用户名不能为空')
        if not email:
            raise ValueError('邮箱不能为空')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """用户模型"""
    
    ROLE_CHOICES = [
        ('school', '学校用户'),
        ('admin', '管理员'),
        ('region_admin', '区域管理员'),
    ]
    
    username = models.CharField('用户名', max_length=50, unique=True)
    email = models.EmailField('邮箱', unique=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='school')
    is_active = models.BooleanField('是否激活', default=True)
    is_staff = models.BooleanField('是否为员工', default=False)
    is_locked = models.BooleanField('是否锁定', default=False)
    locked_until = models.DateTimeField('锁定截止时间', null=True, blank=True)
    last_login = models.DateTimeField('最后登录时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return self.username
    
    def is_school_user(self):
        """是否为学校用户"""
        return self.role == 'school'
    
    def is_admin_user(self):
        """是否为管理员"""
        return self.role == 'admin'

    def is_region_admin(self):
        """是否为区域管理员"""
        return self.role == 'region_admin'

    def is_admin(self):
        """是否为管理员"""
        return self.role == 'region_admin' or self.role == 'admin'

    def check_locked(self):
        """检查账号是否被锁定"""
        if self.is_locked and self.locked_until:
            if timezone.now() > self.locked_until:
                # 锁定时间已过，解锁账号
                self.is_locked = False
                self.locked_until = None
                self.save(update_fields=['is_locked', 'locked_until'])
                return False
            return True
        return self.is_locked
