"""
统一响应格式工具
"""
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(data=None, message='success', status_code=status.HTTP_200_OK):
        """成功响应"""
        response_data = {
            'success': True,
            'message': message,
        }
        if data is not None:
            response_data['data'] = data
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(message='error', code='ERROR', details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """错误响应"""
        response_data = {
            'success': False,
            'error': {
                'code': code,
                'message': message,
            }
        }
        if details:
            response_data['error']['details'] = details
        return Response(response_data, status=status_code)
    
    @staticmethod
    def paginated_response(queryset, serializer_class, request):
        """分页响应"""
        from rest_framework.pagination import PageNumberPagination
        
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)
