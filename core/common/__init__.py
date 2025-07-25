"""
Spider项目公共模块

提供统一的日志、HTTP请求、工具函数等公共组件
"""

__version__ = "1.0.0"
__author__ = "Spider Project"

from .logger import get_logger, setup_logging
from .http_client import HttpClient
from .utils import ensure_dir, save_to_csv, load_json, save_json

__all__ = [
    'get_logger',
    'setup_logging', 
    'HttpClient',
    'ensure_dir',
    'save_to_csv',
    'load_json',
    'save_json'
]