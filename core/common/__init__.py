"""
Spider项目公共模块

提供统一的日志、HTTP请求、工具函数等公共组件
"""

__version__ = "1.0.0"
__author__ = "Spider Project"

from .logger import get_logger, setup_logging
from .utils import ensure_dir, save_to_csv, load_json, save_json

# 可选导入 - 如果依赖不存在则忽略
try:
    from .http_client import HttpClient
    _http_client_available = True
except ImportError:
    HttpClient = None
    _http_client_available = False

__all__ = [
    'get_logger',
    'setup_logging', 
    'ensure_dir',
    'save_to_csv',
    'load_json',
    'save_json'
]

if _http_client_available:
    __all__.append('HttpClient')