"""
阿里云OSS存储后端 - 兼容Django 4.x
"""
import os
import oss2
from datetime import datetime
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible


@deconstructible
class AliyunOSSStorage(Storage):
    """
    阿里云OSS存储后端
    """
    
    def __init__(self):
        self.access_key_id = getattr(settings, 'ALIYUN_OSS_ACCESS_KEY_ID', '')
        self.access_key_secret = getattr(settings, 'ALIYUN_OSS_ACCESS_KEY_SECRET', '')
        self.endpoint = getattr(settings, 'ALIYUN_OSS_ENDPOINT', '')
        self.bucket_name = getattr(settings, 'ALIYUN_OSS_BUCKET_NAME', '')
        self.cname = getattr(settings, 'ALIYUN_OSS_CNAME', '')
        
        # 初始化OSS认证和Bucket
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        
        # 构建基础URL
        if self.cname:
            self.base_url = self.cname.rstrip('/')
        else:
            # 从endpoint提取域名
            endpoint_host = self.endpoint.replace('https://', '').replace('http://', '')
            self.base_url = f"https://{self.bucket_name}.{endpoint_host}"
    
    def _get_key_name(self, name):
        """获取OSS中的key名称"""
        return name.lstrip('/')
    
    def _open(self, name, mode='rb'):
        """打开文件"""
        key = self._get_key_name(name)
        result = self.bucket.get_object(key)
        return ContentFile(result.read())
    
    def _save(self, name, content):
        """保存文件到OSS"""
        key = self._get_key_name(name)
        
        # 读取文件内容
        if hasattr(content, 'read'):
            data = content.read()
        else:
            data = content
        
        # 上传到OSS
        self.bucket.put_object(key, data)
        
        return name
    
    def delete(self, name):
        """删除文件"""
        key = self._get_key_name(name)
        self.bucket.delete_object(key)
    
    def exists(self, name):
        """检查文件是否存在"""
        key = self._get_key_name(name)
        return self.bucket.object_exists(key)
    
    def listdir(self, path):
        """列出目录内容"""
        path = self._get_key_name(path)
        if path and not path.endswith('/'):
            path += '/'
        
        dirs = []
        files = []
        
        for obj in oss2.ObjectIterator(self.bucket, prefix=path, delimiter='/'):
            if obj.is_prefix():
                dirs.append(obj.key[len(path):].rstrip('/'))
            else:
                files.append(obj.key[len(path):])
        
        return dirs, files
    
    def size(self, name):
        """获取文件大小"""
        key = self._get_key_name(name)
        meta = self.bucket.get_object_meta(key)
        return meta.content_length
    
    def url(self, name):
        """获取文件URL"""
        key = self._get_key_name(name)
        return f"{self.base_url}/{key}"
    
    def get_accessed_time(self, name):
        """获取访问时间（OSS不支持，返回修改时间）"""
        return self.get_modified_time(name)
    
    def get_created_time(self, name):
        """获取创建时间（OSS不支持，返回修改时间）"""
        return self.get_modified_time(name)
    
    def get_modified_time(self, name):
        """获取修改时间"""
        key = self._get_key_name(name)
        meta = self.bucket.get_object_meta(key)
        return datetime.strptime(
            meta.headers['Last-Modified'],
            '%a, %d %b %Y %H:%M:%S %Z'
        )
