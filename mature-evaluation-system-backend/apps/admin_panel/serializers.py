"""
管理员功能序列化器
"""
from rest_framework import serializers
from .models import ContentPage, SystemConfig, OperationLog, News


class NewsSerializer(serializers.ModelSerializer):
    """实践动态序列化器"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    cover_image = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = News
        fields = ['id', 'title', 'summary', 'content', 'cover_image', 'cover_image_url', 
                  'publish_date', 'author', 'author_name', 'is_published', 'view_count', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'author_name', 'view_count', 'created_at', 'updated_at']
    
    def get_cover_image_url(self, obj):
        """获取封面图片URL"""
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None
    
    def create(self, validated_data):
        """创建实践动态"""
        # 处理cover_image字段
        cover_image_path = validated_data.pop('cover_image', None)
        news = News.objects.create(**validated_data)
        
        # 如果有封面图片路径，设置它
        if cover_image_path:
            news.cover_image = cover_image_path
            news.save()
        
        return news
    
    def update(self, instance, validated_data):
        """更新实践动态"""
        # 处理cover_image字段
        cover_image_path = validated_data.pop('cover_image', None)
        
        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 如果有封面图片路径，更新它
        if cover_image_path is not None:
            instance.cover_image = cover_image_path
        
        instance.save()
        return instance


class ContentPageSerializer(serializers.ModelSerializer):
    """内容页面序列化器"""
    
    class Meta:
        model = ContentPage
        fields = ['id', 'page_key', 'title', 'content', 'order', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器"""
    
    class Meta:
        model = SystemConfig
        fields = ['id', 'config_key', 'config_value', 'config_type', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = ['id', 'user', 'username', 'operation_type', 'operation_desc', 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['id', 'created_at']
