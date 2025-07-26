"""
自定义异常类
定义项目中使用的各种异常类型
"""

from typing import Optional, Dict, Any


class SpiderError(Exception):
    """爬虫基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class HttpError(SpiderError):
    """HTTP请求相关异常"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 url: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.url = url


class ParseError(SpiderError):
    """数据解析异常"""
    
    def __init__(self, message: str, source_data: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.source_data = source_data


class ValidationError(SpiderError):
    """数据验证异常"""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value


class ConfigError(SpiderError):
    """配置相关异常"""
    pass


class SecurityError(SpiderError):
    """安全相关异常"""
    pass


class RateLimitError(SpiderError):
    """请求频率限制异常"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class AuthenticationError(SpiderError):
    """认证相关异常"""
    pass


class AuthorizationError(SpiderError):
    """授权相关异常"""
    pass


class DataSaveError(SpiderError):
    """数据保存异常"""
    
    def __init__(self, message: str, filepath: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.filepath = filepath


class NetworkError(SpiderError):
    """网络连接异常"""
    pass


class TimeoutError(SpiderError):
    """超时异常"""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds


class RetryExhaustedError(SpiderError):
    """重试次数耗尽异常"""
    
    def __init__(self, message: str, attempts: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.attempts = attempts