"""
错误处理模块 - Phase 6: 结构化失败处理
"""
from typing import Dict, Optional, Tuple
import traceback


class ErrorCategory:
    """错误类别枚举"""
    NETWORK = 'NETWORK'      # 网络错误
    API = 'API'              # API错误
    IO = 'IO'                # 文件IO错误
    VALIDATION = 'VALIDATION'  # 验证错误
    TIMEOUT = 'TIMEOUT'      # 超时错误
    UNKNOWN = 'UNKNOWN'      # 未知错误


class ErrorHandler:
    """结构化错误处理器"""
    
    # 可重试的错误代码
    RETRIABLE_ERROR_CODES = {
        'NETWORK_ERROR',
        'TIMEOUT',
        'RATE_LIMIT',
        'SERVER_ERROR',
        'CONNECTION_ERROR',
        'TEMPORARY_FAILURE'
    }
    
    # 不可重试的错误代码
    NON_RETRIABLE_ERROR_CODES = {
        'AUTHENTICATION_ERROR',
        'INVALID_REQUEST',
        'VALIDATION_ERROR',
        'FILE_NOT_FOUND',
        'PERMISSION_DENIED',
        'QUOTA_EXCEEDED'
    }
    
    @staticmethod
    def classify_error(exception: Exception, error_message: str = None) -> Tuple[str, str, str, bool]:
        """
        Phase 6: 分类错误并返回结构化信息
        
        Args:
            exception: 异常对象
            error_message: 错误消息（可选）
        
        Returns:
            (failure_type, error_code, error_message, is_retriable)
        """
        error_str = str(exception).lower()
        error_type = type(exception).__name__
        error_msg = error_message or str(exception)
        
        # 网络错误
        if any(keyword in error_str for keyword in ['connection', 'network', 'dns', 'resolve', 'refused']):
            return ErrorCategory.NETWORK, 'NETWORK_ERROR', error_msg, True
        
        # 超时错误
        if any(keyword in error_str for keyword in ['timeout', 'timed out', 'time out']):
            return ErrorCategory.TIMEOUT, 'TIMEOUT', error_msg, True
        
        # API错误
        if any(keyword in error_str for keyword in ['api', 'http', 'status code', '401', '403', '404', '429', '500', '502', '503']):
            if '401' in error_str or 'authentication' in error_str or 'unauthorized' in error_str:
                return ErrorCategory.API, 'AUTHENTICATION_ERROR', error_msg, False
            elif '403' in error_str or 'forbidden' in error_str:
                return ErrorCategory.API, 'PERMISSION_DENIED', error_msg, False
            elif '429' in error_str or 'rate limit' in error_str:
                return ErrorCategory.API, 'RATE_LIMIT', error_msg, True
            elif '500' in error_str or '502' in error_str or '503' in error_str:
                return ErrorCategory.API, 'SERVER_ERROR', error_msg, True
            elif '404' in error_str or 'not found' in error_str:
                return ErrorCategory.API, 'INVALID_REQUEST', error_msg, False
            else:
                return ErrorCategory.API, 'API_ERROR', error_msg, True
        
        # IO错误
        if any(keyword in error_str for keyword in ['file', 'io', 'permission', 'access', 'read', 'write', 'not found']):
            if 'not found' in error_str or 'no such file' in error_str:
                return ErrorCategory.IO, 'FILE_NOT_FOUND', error_msg, False
            elif 'permission' in error_str or 'access' in error_str:
                return ErrorCategory.IO, 'PERMISSION_DENIED', error_msg, False
            else:
                return ErrorCategory.IO, 'IO_ERROR', error_msg, True
        
        # 验证错误
        if any(keyword in error_str for keyword in ['invalid', 'validation', 'format', 'decode', 'parse']):
            return ErrorCategory.VALIDATION, 'VALIDATION_ERROR', error_msg, False
        
        # 未知错误
        return ErrorCategory.UNKNOWN, 'UNKNOWN_ERROR', error_msg, False
    
    @staticmethod
    def is_retriable(error_code: str) -> bool:
        """判断错误是否可重试"""
        if error_code in ErrorHandler.RETRIABLE_ERROR_CODES:
            return True
        if error_code in ErrorHandler.NON_RETRIABLE_ERROR_CODES:
            return False
        # 默认：网络、超时、服务器错误可重试
        return error_code.startswith('NETWORK') or error_code.startswith('TIMEOUT') or error_code.startswith('SERVER')
    
    @staticmethod
    def format_error_details(exception: Exception) -> Dict[str, str]:
        """
        格式化错误详情
        
        Returns:
            {
                'failure_type': str,
                'error_code': str,
                'error_message': str,
                'is_retriable': bool,
                'traceback': str (可选)
            }
        """
        failure_type, error_code, error_message, is_retriable = ErrorHandler.classify_error(exception)
        
        result = {
            'failure_type': failure_type,
            'error_code': error_code,
            'error_message': error_message,
            'is_retriable': is_retriable
        }
        
        # 添加详细堆栈（用于调试）
        try:
            result['traceback'] = traceback.format_exc()
        except:
            pass
        
        return result

